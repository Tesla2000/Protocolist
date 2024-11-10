from __future__ import annotations

import re
from functools import reduce
from pathlib import Path

import libcst
from more_itertools.more import map_reduce

from ...protocol_markers.types_marker_factory import create_type_marker
from ...transform.class_extractor import ClassExtractor
from ..presentation_option import PresentationOption
from ..replace_partial_with_combined import ReplacePartialWithCombined
from .protocol_saver import ProtocolSaver


class CombinedProtocolSaver(ProtocolSaver):
    type = PresentationOption.COMBINED_PROTOCOLS

    def modify_protocols(self) -> None:
        code = self.config.interfaces_path.read_text()
        new_code = code.partition("@")[0]
        class_extractor = ClassExtractor(create_type_marker(self.config))
        classes = class_extractor.extract_classes(code)
        grouped_classes = map_reduce(
            classes.items(),
            lambda item: re.findall(r"\D+", item[0])[0],
            lambda item: item[1],
        )
        for class_name, instances in grouped_classes.items():
            methods = reduce(
                set.union,
                map(
                    lambda instance: set(
                        filter(
                            lambda line: line.startswith("    def "),
                            instance.splitlines(),
                        )
                    ),
                    instances,
                ),
            )
            fields = reduce(
                set.union,
                map(
                    lambda instance: set(
                        filter(
                            lambda line: re.findall(r"^    \w+\:", line),
                            instance.splitlines(),
                        )
                    ),
                    instances,
                ),
            )
            indent = 2 * self.config.tab_length * " "
            new_code = (
                f"\n@runtime_checkable\nclass {class_name}(Protocol):"
                f"\n{'\n'.join(fields)}"
                f"{'\n'.join(f"{method}\n{indent}..." for method in methods)}"
            )
        partial2composite = {
            class_name: re.findall(r"\D+", class_name)[0]
            for class_name in classes.keys()
        }
        for partial, composite in partial2composite.items():
            new_code = new_code.replace(partial, composite)
        self.config.interfaces_path.write_text(new_code)
        for filepath in filter(
            lambda path: path.suffix == ".py", map(Path, self.config.pos_args)
        ):
            filepath.write_text(
                libcst.parse_module(filepath.read_text())
                .visit(
                    ReplacePartialWithCombined(self.config, partial2composite)
                )
                .code
            )
