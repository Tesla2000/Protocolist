from __future__ import annotations

from collections import OrderedDict
from pathlib import Path
from typing import Optional

import libcst
from libcst import ClassDef
from libcst import Module

from src.interfacer.config import Config
from src.interfacer.extract_bases import extract_bases
from src.interfacer.protocol_markers.marker import TypeMarker
from src.interfacer.protocol_markers.types_marker_factory import (
    create_type_marker,
)
from src.interfacer.transform.import_visiting_transformer import (
    ImportVisitingTransformer,
)


class ClassExtractor(ImportVisitingTransformer):
    classes: dict[str, str]
    protocols: dict[str, str]
    class_nodes: OrderedDict[str, ClassDef]

    def __init__(
        self, config: Config, type_marker: Optional[TypeMarker] = None
    ):
        super().__init__(config, type_marker)
        self.classes = {}
        self.protocols = {}
        self.class_nodes = OrderedDict()
        self._internal_classes = {}

    def visit_ClassDef(self, node: "ClassDef") -> Optional[bool]:
        class_name = node.name.value
        class_code = (
            self.classes.get(class_name, Module([node]).code)
            .lstrip()
            .replace(self.config.tab_length * " ", "\t")
        )
        if any(map("Protocol".__eq__, extract_bases(node))):
            self.protocols[class_name] = class_code
        if (class_name, class_code) in self._internal_classes.items():
            return super().visit_ClassDef(node)
        self.class_nodes[class_name] = node
        self.classes[class_name] = class_code
        self._update_internal_classes(node)
        return super().visit_ClassDef(node)

    def extract_classes(self, code) -> dict[str, str]:
        module = libcst.parse_module(
            code.replace(self.config.tab_length * " ", "\t")
        )
        module.visit(self)
        return self.classes

    def extract_protocols(self, code) -> dict[str, str]:
        module = libcst.parse_module(
            code.replace(self.config.tab_length * " ", "\t")
        )
        module.visit(self)
        return self.protocols

    @property
    def imports(self):
        return self.type_marker.imports

    @property
    def imported_interfaces(self):
        return self.type_marker.imported_interfaces

    def _update_internal_classes(self, node: ClassDef):
        visitor = type(self)(self.config, self.type_marker)
        node.body.visit(visitor)
        self._internal_classes.update(visitor.classes)


class GlobalClassExtractor:
    extractors: dict[Path, ClassExtractor]

    def __init__(self, config: Config):
        self.config = config
        self.extractors = {}

    def get(self, path: Path) -> ClassExtractor:
        if path in self.extractors:
            return self.extractors[path]
        self.extractors[path] = ClassExtractor(
            self.config, create_type_marker(self.config)
        )
        self.extractors[path].extract_classes(path.read_text())
        return self.extractors[path]
