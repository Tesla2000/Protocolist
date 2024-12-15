from __future__ import annotations

from typing import Optional

from libcst import ClassDef
from libcst import MaybeSentinel

from ..config import Config
from ..protocol_markers.marker import TypeMarker
from .import_visiting_transformer import ImportVisitingTransformer


class InheritanceRemover(ImportVisitingTransformer):
    def __init__(
        self, config: Config, type_marker: Optional[TypeMarker] = None
    ):
        super().__init__(config, type_marker)
        self.updated_module = None

    def leave_ClassDef(
        self, original_node: "ClassDef", updated_node: "ClassDef"
    ) -> "ClassDef":
        bases = tuple(
            filter(
                lambda arg: getattr(arg.value, "value", None)
                not in (
                    self.type_marker.imported_interfaces_as.get(
                        interface, interface
                    )
                    for interface in self.type_marker.imported_interfaces
                ),
                updated_node.bases,
            )
        )
        updated_node = updated_node.with_changes(bases=bases)
        if not bases:
            return updated_node.with_changes(
                rpar=MaybeSentinel.DEFAULT, lpar=MaybeSentinel.DEFAULT
            )
        return updated_node
