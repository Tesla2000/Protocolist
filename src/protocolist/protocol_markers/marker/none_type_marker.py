from __future__ import annotations

from libcst import Param

from ...protocol_dict import ProtocolDict
from ...protocol_markers.mark_options import MarkOption
from ...protocol_markers.marker.type_marker import TypeMarker


class NoneTypeMarker(TypeMarker):
    type = MarkOption.NONE

    def conv_parameter(
        self, updated_node: "Param", protocols: ProtocolDict, annotations: dict
    ) -> "Param":
        return updated_node
