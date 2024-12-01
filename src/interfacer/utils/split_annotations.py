from __future__ import annotations

from typing import Optional

import libcst
from libcst import Name


def split_annotations(annotation: str) -> list[str]:
    names_getter = _NamesGetter()
    libcst.parse_expression(annotation).visit(names_getter)
    return names_getter.names


class _NamesGetter(libcst.CSTTransformer):
    def __init__(self):
        super().__init__()
        self.names = []

    def visit_Name(self, node: "Name") -> Optional[bool]:
        self.names.append(node.value)
        return super().visit_Name(node)
