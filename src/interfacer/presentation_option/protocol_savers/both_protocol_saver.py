from __future__ import annotations

import re

from more_itertools.more import map_reduce

from ...protocol_markers.types_marker_factory import create_type_marker
from ...transform.class_extractor import ClassExtractor
from ..presentation_option import PresentationOption
from .protocol_saver import ProtocolSaver


class BothProtocolSaver(ProtocolSaver):
    type = PresentationOption.BOTH

    def _modify_protocols(self) -> None:
        code = self.config.interfaces_path.read_text()
        new_code = code
        class_extractor = ClassExtractor(
            self.config, create_type_marker(self.config)
        )
        classes = class_extractor.extract_classes(code)
        partial2composite = {
            class_name: re.findall(r"\D+", class_name)[0]
            for class_name in classes.keys()
        }
        grouped_classes = map_reduce(
            partial2composite.items(),
            lambda item: item[1],
            lambda item: item[0],
        )
        for class_name, instances in grouped_classes.items():
            new_protocol = (
                f"@runtime_checkable\nclass {class_name}("
                f"{', '.join(instances)}, Protocol):\n    pass"
            )
            new_code += "\n" + new_protocol
        self.config.interfaces_path.write_text(new_code)
