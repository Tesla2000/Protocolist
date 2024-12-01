from __future__ import annotations

from typing import Optional

import libcst
from libcst import Import
from libcst import ImportFrom

from ..config import Config
from ..protocol_markers.marker import TypeMarker
from ..protocol_markers.types_marker_factory import (
    create_type_marker,
)


class ImportVisitingTransformer(libcst.CSTTransformer):
    def __init__(
        self, config: Config, type_marker: Optional[TypeMarker] = None
    ):
        super().__init__()
        self.type_marker = type_marker or create_type_marker(config)
        self.config = config

    def visit_Import(self, node: "Import") -> Optional[bool]:
        self.type_marker.register_import(node)
        return super().visit_Import(node)

    def visit_ImportFrom(self, node: "ImportFrom") -> Optional[bool]:
        self.type_marker.register_import(node)
        return super().visit_ImportFrom(node)
