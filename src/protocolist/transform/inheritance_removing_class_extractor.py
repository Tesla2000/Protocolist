from __future__ import annotations

from typing import Optional

import libcst
from libcst import ClassDef
from libcst import MaybeSentinel
from libcst import Module

from ..config import Config
from ..protocol_markers.marker import TypeMarker
from ..transform.class_extractor import ClassExtractor


class InheritanceRemovingClassExtractor(ClassExtractor):
    def __init__(
        self, config: Config, type_marker: Optional[TypeMarker] = None
    ):
        super().__init__(config, type_marker)
        self.updated_module = None

    def leave_ClassDef(
        self, original_node: "ClassDef", updated_node: "ClassDef"
    ) -> "ClassDef":
        class_name = updated_node.name.value
        self.classes[class_name] = self.classes.get(
            class_name, Module([updated_node]).code
        )
        bases = tuple(
            filter(
                lambda arg: getattr(arg.value, "value", None)
                not in self.type_marker.imported_interfaces,
                updated_node.bases,
            )
        )
        updated_node = updated_node.with_changes(bases=bases)
        if not bases:
            return updated_node.with_changes(
                rpar=MaybeSentinel.DEFAULT, lpar=MaybeSentinel.DEFAULT
            )
        return updated_node

    def extract_classes(self, code) -> dict[str, str]:
        module = libcst.parse_module(code)
        self.updated_module = module.visit(self)
        return self.classes
