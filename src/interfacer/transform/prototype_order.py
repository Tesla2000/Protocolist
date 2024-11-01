from __future__ import annotations

from libcst import ClassDef
from libcst import Module
from mypyc.subtype import annotations

from ..config import Config
from .transformer import Transformer


class PrototypeOrder(Transformer):
    def __init__(
        self, module: Module, config: Config, inheritances: dict[str, str]
    ):
        super().__init__(module, config)
        self.inheritances = inheritances

    def leave_ClassDef(
        self, original_node: "ClassDef", updated_node: "ClassDef"
    ) -> "ClassDef":
        return updated_node
