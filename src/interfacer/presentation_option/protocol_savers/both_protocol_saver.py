from __future__ import annotations

import re
import string

from more_itertools.more import map_reduce

from ...consts import protocol_replacement_name
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
            class_name: re.sub(r"\d+", "", class_name)
            for class_name in classes.keys()
            if any(map(string.digits.__contains__, class_name))
        }
        grouped_classes = map_reduce(
            partial2composite.items(),
            lambda item: item[1],
            lambda item: item[0],
        )
        for class_name, instances in grouped_classes.items():
            new_protocol = (
                f"@runtime_checkable\nclass {class_name}("
                f"{', '.join(instances)}, "
                f"{protocol_replacement_name}):\n\tpass"
            )
            new_code += "\n" + new_protocol
        self.config.interfaces_path.write_text(new_code)
