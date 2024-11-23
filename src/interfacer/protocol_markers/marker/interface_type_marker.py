from __future__ import annotations

from libcst import Param

from src.interfacer.protocol_dict import ProtocolDict
from src.interfacer.protocol_markers.mark_options import MarkOption
from src.interfacer.protocol_markers.marker.type_marker import TypeMarker


class InterfaceTypeMarker(TypeMarker):
    type = MarkOption.INTERFACE

    def conv_parameter(
        self, updated_node: "Param", protocols: ProtocolDict, annotations: dict
    ) -> "Param":
        if updated_node.annotation is None:
            return updated_node.with_changes(
                annotation=self._create_literal_annotation(
                    updated_node, protocols, annotations
                )
            )
        annotation = updated_node.annotation.annotation.value
        if annotation in self.imported_interfaces:
            return updated_node.with_changes(
                annotation=self._create_literal_annotation(
                    updated_node, protocols, annotations
                )
            )
        return updated_node
