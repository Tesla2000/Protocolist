from __future__ import annotations

from libcst import Annotation
from libcst import ImportFrom
from libcst import Module
from libcst import Name

from ...interfacer.transform.transformer import Transformer
from ..annotation2string import subscript_element2string
from ..config import Config


class ReplaceImportsAndNames(Transformer):
    def __init__(self, config: Config, replace_dictionary: dict[str, str]):
        super().__init__()
        self.config = config
        self.replace_dictionary = replace_dictionary

    def leave_ImportFrom(
        self, original_node: "ImportFrom", updated_node: "ImportFrom"
    ) -> "ImportFrom":
        if (
            Module([updated_node]).code.split()[1]
            == self.config.interface_import_path
        ):
            return updated_node.with_changes(
                names=tuple(
                    import_alias.with_changes(
                        name=import_alias.name.with_changes(
                            value=self.replace_dictionary.get(
                                import_alias.name.value,
                                import_alias.name.value,
                            )
                        )
                    )
                    for import_alias in updated_node.names
                )
            )
        return updated_node

    def leave_Name(
        self, original_node: "Name", updated_node: "Name"
    ) -> "Name":
        return updated_node.with_changes(
            value=self.replace_dictionary.get(
                updated_node.value, updated_node.value
            )
        )

    def leave_Annotation(
        self, original_node: "Annotation", updated_node: "Annotation"
    ) -> "Annotation":
        if not hasattr(updated_node.annotation, "slice"):
            return updated_node
        slices = updated_node.annotation.slice
        unique_slices = tuple(
            dict(zip(map(subscript_element2string, slices), slices)).values()
        )
        if len(unique_slices) > 1:
            return updated_node.with_changes(
                annotation=updated_node.annotation.with_changes(
                    slice=unique_slices
                )
            )
        return updated_node.with_changes(
            annotation=Name(value=subscript_element2string(unique_slices[0]))
        )
