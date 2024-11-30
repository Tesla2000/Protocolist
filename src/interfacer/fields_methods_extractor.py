from __future__ import annotations

from collections.abc import Sequence
from typing import NamedTuple
from typing import Optional

import libcst
from libcst import AnnAssign
from libcst import ClassDef
from libcst import FunctionDef
from libcst import Module

from src.interfacer.extract_bases import extract_bases


class _MethodsAndFields(NamedTuple):
    methods: Sequence[str]
    fields: Sequence[str]


class _MethodsFieldsAndBases(NamedTuple):
    methods: Sequence[str]
    fields: Sequence[str]
    bases: Sequence[str]


class FieldsAndMethodsExtractor(libcst.CSTTransformer):
    def __init__(self):
        super().__init__()
        self.methods = set()
        self.fields = set()
        self.bases = set()

    def visit_FunctionDef(self, node: "FunctionDef") -> Optional[bool]:
        self.methods.add(Module([node]).code)
        return super().visit_FunctionDef(node)

    def visit_AnnAssign(self, node: "AnnAssign") -> Optional[bool]:
        self.fields.add(Module([node]).code)
        return super().visit_AnnAssign(node)

    def visit_ClassDef(self, node: "ClassDef") -> None:
        self.bases = set(extract_bases(node))
        return super().visit_ClassDef(node)

    @classmethod
    def get_methods_and_fields(cls, code: str) -> _MethodsAndFields:
        extractor = cls()
        libcst.parse_module(code).visit(extractor)
        return _MethodsAndFields(
            tuple(extractor.methods), tuple(extractor.fields)
        )

    @classmethod
    def get_methods_fields_and_bases(cls, code: str) -> _MethodsFieldsAndBases:
        extractor = cls()
        libcst.parse_module(code).visit(extractor)
        return _MethodsFieldsAndBases(
            tuple(extractor.methods),
            tuple(extractor.fields),
            tuple(extractor.bases),
        )
