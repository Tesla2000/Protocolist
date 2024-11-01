from __future__ import annotations

from typing import Optional

from libcst import ClassDef
from libcst import Module

from ..config import Config
from .transformer import Transformer


class PrototypeExtractor(Transformer):
    prototypes: dict[str, str]

    def __init__(self, module: Module, config: Config):
        super().__init__(module, config)
        self.prototypes = {}

    def visit_ClassDef(self, node: "ClassDef") -> Optional[bool]:
        class_name = node.name.value
        self.prototypes[class_name] = self.prototypes.get(
            class_name, Module([node]).code
        )
        return super().visit_ClassDef(node)
