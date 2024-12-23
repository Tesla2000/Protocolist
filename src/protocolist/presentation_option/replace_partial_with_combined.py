from __future__ import annotations

from itertools import chain
from typing import Optional

import libcst
from libcst import Annotation
from libcst import BaseExpression
from libcst import ClassDef
from libcst import CSTTransformer
from libcst import ImportFrom
from libcst import Module
from libcst import Name
from libcst import Subscript

from ..config import Config
from ..consts import grouped_types


class ReplaceNames(CSTTransformer):
    def __init__(self, config: Config, replace_dictionary: dict[str, str]):
        super().__init__()
        self.config = config
        self.replace_dictionary = replace_dictionary.copy()
        self._annotation_names = set()
        self.applicable_groups = set()

    def visit_Annotation(self, node: "Annotation") -> Optional[bool]:
        name_gatherer = _AnnotationNamesGatherer()
        node.visit(name_gatherer)
        self._annotation_names.update(name_gatherer.annotation_names)
        return super().visit_Annotation(node)

    def visit_ClassDef(self, node: "ClassDef") -> Optional[bool]:
        class_name = node.name.value
        if class_name in self.replace_dictionary:
            del self.replace_dictionary[class_name]
        return super().visit_ClassDef(node)

    def leave_Name(
        self, original_node: "Name", updated_node: "Name"
    ) -> "Name":
        value = updated_node.value
        if (
            value == self.replace_dictionary.get(value, value)
            or original_node not in self._annotation_names
        ):
            return updated_node
        return libcst.parse_expression(self.replace_dictionary[value])

    def leave_Subscript(
        self, original_node: "Subscript", updated_node: "Subscript"
    ) -> "BaseExpression":
        """Deduplication"""
        name = Module([updated_node]).code.partition("[")[0]
        if name != "Union":
            return updated_node
        types = set(
            Module([slice]).code.strip(", \n") for slice in updated_node.slice
        )
        applicable_groups = tuple(
            filter(
                lambda group: all(map(types.__contains__, group.str_types)),
                grouped_types,
            )
        )
        group_names = tuple(group.name for group in applicable_groups)
        types.difference_update(
            chain.from_iterable(group.str_types for group in applicable_groups)
        )
        types.update(group_names)
        self.applicable_groups.update(applicable_groups)
        types = sorted(types)
        if len(types) > 1:
            return libcst.parse_expression(f'{name}[{", ".join(types)}]')
        return libcst.parse_expression(types[0])


class ReplaceImportsAndNames(ReplaceNames):
    def __init__(
        self,
        config: Config,
        replace_dictionary: dict[str, str],
        import_as: dict[str, str],
    ):
        super().__init__(config, import_as)
        self.original_names = replace_dictionary

    def leave_ImportFrom(
        self, original_node: "ImportFrom", updated_node: "ImportFrom"
    ) -> "ImportFrom":
        code = Module([original_node]).code
        from_, import_path, import_, element, *_ = code.split()
        if import_path == self.config.interface_import_path and not _:
            as_name = self.replace_dictionary.get(element, element)
            original_name = self.original_names.get(element, element)
            return libcst.parse_statement(
                f"from {import_path} import {original_name}"
                + (as_name != original_name) * f" as {as_name}"
            ).body[0]
        return updated_node


class _AnnotationNamesGatherer(CSTTransformer):
    def __init__(self):
        super().__init__()
        self.annotation_names = set()

    def visit_Name(self, node: "Name") -> Optional[bool]:
        self.annotation_names.add(node)
        return super().visit_Name(node)
