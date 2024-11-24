from __future__ import annotations

from collections import OrderedDict
from pathlib import Path
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
    class_nodes: OrderedDict[str, ClassDef]

    def __init__(self, type_marker: TypeMarker):
        super().__init__(type_marker)
        self.classes = {}
        self.class_nodes = OrderedDict()

    def visit_ClassDef(self, node: "ClassDef") -> Optional[bool]:
        class_name = node.name.value
        self.class_nodes[class_name] = node
        self.classes[class_name] = self.classes.get(
            class_name, Module([node]).code
        ).lstrip()
        return super().visit_ClassDef(node)

    def extract_classes(self, code) -> dict[str, str]:
        module = libcst.parse_module(code)
        module.visit(self)
        return self.classes

    @property
    def imports(self):
        return self.type_marker.imports

    @property
    def imported_interfaces(self):
        return self.type_marker.imported_interfaces


class GlobalClassExtractor:
    extractors: dict[Path, ClassExtractor]

    def __init__(self, type_marker: TypeMarker):
        self.type_marker = type_marker
        self.extractors = {}

    def get(self, path: Path) -> ClassExtractor:
        if path in self.extractors:
            return self.extractors[path]
        self.extractors[path] = ClassExtractor(self.type_marker)
        self.extractors[path].extract_classes(path.read_text())
        return self.extractors[path]
