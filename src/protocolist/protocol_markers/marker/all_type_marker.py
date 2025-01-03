from __future__ import annotations

from libcst import Param

from ...protocol_dict import ProtocolDict
from ...protocol_markers.mark_options import MarkOption
from ...protocol_markers.marker.type_marker import TypeMarker


class AllTypeMarker(TypeMarker):
    type = MarkOption.ALL

    def conv_parameter(
        self, updated_node: "Param", protocols: ProtocolDict, annotations: dict
    ) -> "Param":
        return updated_node.with_changes(
            annotation=self._create_literal_annotation(
                updated_node, protocols, annotations
            )
        )
