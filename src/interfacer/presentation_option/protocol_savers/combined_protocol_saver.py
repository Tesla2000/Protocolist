from __future__ import annotations

import re
from functools import reduce

from more_itertools.more import map_reduce

from ...protocol_markers.types_marker_factory import create_type_marker
from ...transform.class_extractor import ClassExtractor
from ..presentation_option import PresentationOption
from .protocol_saver import ProtocolSaver


class CombinedProtocolSaver(ProtocolSaver):
    type = PresentationOption.COMBINED_PROTOCOLS

    def _modify_protocols(self) -> None:
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
                        re.findall(r"    def [^\(]+\([^\)]+\):", instance)
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
            new_code += (
                f"\n@runtime_checkable\nclass {class_name}(Protocol):"
                f"\n{'\n'.join(fields)}"
                f"{'\n'.join(f"{method.rstrip('.')}"
                             f"\n{indent}..." for method in methods)}"
            )
        partial2composite = {
            class_name: re.findall(r"\D+", class_name)[0]
            for class_name in classes.keys()
        }
        self.replace_dictionary = {
            **partial2composite,
            **{
                key: re.findall(r"\D+", value)[0]
                for key, value in self.replace_dictionary.items()
            },
        }
        for partial, composite in partial2composite.items():
            new_code = new_code.replace(partial, composite)
        self.config.interfaces_path.write_text(new_code)
