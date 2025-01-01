from __future__ import annotations

from collections import OrderedDict
from contextlib import suppress
from pathlib import Path
from typing import Optional

import libcst
from libcst import ClassDef
from libcst import Module
from libcst import ParserSyntaxError

from ..config import Config
from ..consts import protocol_replacement_name
from ..extract_bases import extract_bases
from ..protocol_markers.marker import TypeMarker
from ..protocol_markers.types_marker_factory import (
    create_type_marker,
)
from ..transform.import_visiting_transformer import (
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
        if any(map(protocol_replacement_name.__eq__, extract_bases(node))):
            self.protocols[class_name] = class_code
        if (class_name, class_code) in self._internal_classes.items():
            return super().visit_ClassDef(node)
        self.class_nodes[class_name] = node
        self.classes[class_name] = class_code
        self._update_internal_classes(node)
        return super().visit_ClassDef(node)

    def extract_classes(self, code: str) -> dict[str, str]:
        for tab_length in (4, 2, 8):
            with suppress(ParserSyntaxError):
                self.config.tab_length = tab_length
                module = libcst.parse_module(
                    code.replace(self.config.tab_length * " ", "\t")
                )
                break
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
        self.config.tab_lengths[path] = self.config.tab_length
        return self.extractors[path]
