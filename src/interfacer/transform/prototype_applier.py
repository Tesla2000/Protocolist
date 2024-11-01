from __future__ import annotations

from typing import Union

from libcst import Annotation
from libcst import FlattenSentinel
from libcst import MaybeSentinel
from libcst import Module
from libcst import Name
from libcst import Param
from libcst import RemovalSentinel
from libcst import SimpleWhitespace
from mypyc.subtype import annotations

from ..config import Config
from .transformer import Transformer


class PrototypeApplier(Transformer):
    def __init__(
        self, module: Module, config: Config, annotations: dict[str, str]
    ):
        super().__init__(module, config)
        self.annotations = annotations

    def leave_Param(
        self, original_node: "Param", updated_node: "Param"
    ) -> Union[
        "Param", MaybeSentinel, FlattenSentinel["Param"], RemovalSentinel
    ]:
        try:
            annotation = updated_node.annotation.annotation.slice[
                0
            ].slice.value.evaluated_value
        except AttributeError:
            return updated_node
        if annotation not in self.annotations:
            return updated_node
        return updated_node.with_changes(
            annotation=Annotation(
                annotation=Name(
                    value=self.annotations[annotation],
                    lpar=[],
                    rpar=[],
                ),
                whitespace_before_indicator=SimpleWhitespace(
                    value="",
                ),
                whitespace_after_indicator=SimpleWhitespace(
                    value=" ",
                ),
            )
        )
