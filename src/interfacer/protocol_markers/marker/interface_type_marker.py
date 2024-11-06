from __future__ import annotations

from libcst import Param, Import, ImportFrom, Module

from src.interfacer.ProtocolDict import ProtocolDict
from src.interfacer.config import Config
from src.interfacer.protocol_markers.mark_options import MarkOption
from src.interfacer.protocol_markers.marker.type_marker import TypeMarker


class InterfaceTypeMarker(TypeMarker):
    type = MarkOption.INTERFACE
    def __init__(self, config: Config):
        super().__init__(config)
        self.imported_interfaces = set()

    def conv_parameter(
        self, updated_node: "Param", protocols: ProtocolDict, annotations: dict
    ) -> "Param":
        if updated_node.annotation is None:
            return updated_node.with_changes(annotation=self._create_literal_annotation(updated_node, protocols, annotations))
        annotation = updated_node.annotation.annotation.value
        if annotation in self.imported_interfaces:
            return updated_node.with_changes(annotation=self._create_literal_annotation(updated_node, protocols, annotations))
        return updated_node

    def register_import(self, import_: Import | ImportFrom):
        if isinstance(import_, ImportFrom):
            import_path, imported_element = Module([import_]).code.split(" ")[1::2]
            if import_path == self.config.interface_import_path and imported_element not in ("Any", ):
                self.imported_interfaces.add(imported_element)
