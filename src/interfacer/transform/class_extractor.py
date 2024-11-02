from __future__ import annotations

from typing import Optional

import libcst
from libcst import ClassDef
from libcst import Module


class ClassExtractor(libcst.CSTTransformer):
    classes: dict[str, str]

    def __init__(self):
        super().__init__()
        self.classes = {}

    def visit_ClassDef(self, node: "ClassDef") -> Optional[bool]:
        class_name = node.name.value
        self.classes[class_name] = self.classes.get(
            class_name, Module([node]).code
        )
        return super().visit_ClassDef(node)

    @classmethod
    def extract_classes(cls, code) -> dict[str, str]:
        module = libcst.parse_module(code)
        transformer = cls()
        module.visit(transformer)
        return transformer.classes
