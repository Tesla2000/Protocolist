from __future__ import annotations

import libcst
from libcst import ImportFrom
from libcst import Module
from libcst import Name
from libcst import Subscript

from ..config import Config
from ..transform.transformer import Transformer


class ReplaceNames(Transformer):
    def __init__(self, config: Config, replace_dictionary: dict[str, str]):
        super().__init__()
        self.config = config
        self.replace_dictionary = replace_dictionary

    def leave_Name(
        self, original_node: "Name", updated_node: "Name"
    ) -> "Name":
        return updated_node.with_changes(
            value=self.replace_dictionary.get(
                updated_node.value, updated_node.value
            )
        )

    def leave_Subscript(
        self, original_node: "Subscript", updated_node: "Subscript"
    ) -> "Subscript":
        """Deduplication"""
        name = Module([updated_node]).code.partition("[")[0]
        if name != "Union":
            return updated_node
        types = sorted(
            set(
                Module([slice]).code.strip(", \n")
                for slice in updated_node.slice
            )
        )
        return libcst.parse_expression(f'{name}[{", ".join(types)}]')


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
        if code.split()[1] == self.config.interface_import_path:
            from_, import_path, import_, element = code.split()
            as_name = self.replace_dictionary.get(element, element)
            original_name = self.original_names.get(element, element)
            return libcst.parse_statement(
                f"from {import_path} import {original_name}"
                + (as_name != original_name) * f" as {as_name}"
            ).body[0]
        return updated_node
