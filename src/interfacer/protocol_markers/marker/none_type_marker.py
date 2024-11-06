from __future__ import annotations

from abc import abstractmethod

from libcst import Param

from src.interfacer.ProtocolDict import ProtocolDict
from src.interfacer.protocol_markers.mark_options import MarkOption
from src.interfacer.protocol_markers.marker.type_marker import TypeMarker


class NoneTypeMarker(TypeMarker):
    type = MarkOption.NONE

    def conv_parameter(
        self, updated_node: "Param", protocols: ProtocolDict, annotations: dict
    ) -> "Param":
        return updated_node
