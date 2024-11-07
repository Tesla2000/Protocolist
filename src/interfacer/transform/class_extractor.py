from __future__ import annotations

from typing import Optional

import libcst
from libcst import ClassDef
from libcst import Module

from src.interfacer.protocol_markers.marker import TypeMarker
from src.interfacer.transform.import_visiting_transformer import (
    ImportVisitingTransformer,
)


class ClassExtractor(ImportVisitingTransformer):
    classes: dict[str, str]

    def __init__(self, type_marker: TypeMarker):
        super().__init__(type_marker)
        self.classes = {}

    def visit_ClassDef(self, node: "ClassDef") -> Optional[bool]:
        class_name = node.name.value
        self.classes[class_name] = self.classes.get(
            class_name, Module([node]).code
        )
        return super().visit_ClassDef(node)

    def extract_classes(self, code) -> dict[str, str]:
        module = libcst.parse_module(code)
        module.visit(self)
        return self.classes
