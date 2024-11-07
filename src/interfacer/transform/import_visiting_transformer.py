from __future__ import annotations

from typing import Optional

import libcst
from libcst import Import
from libcst import ImportFrom

from src.interfacer.protocol_markers.marker import TypeMarker


class ImportVisitingTransformer(libcst.CSTTransformer):
    def __init__(self, type_marker: TypeMarker):
        super().__init__()
        self.type_marker = type_marker

    def visit_Import(self, node: "Import") -> Optional[bool]:
        self.type_marker.register_import(node)
        return super().visit_Import(node)

    def visit_ImportFrom(self, node: "ImportFrom") -> Optional[bool]:
        self.type_marker.register_import(node)
        return super().visit_ImportFrom(node)
