from __future__ import annotations

from typing import Union

import libcst
from libcst import FlattenSentinel
from libcst import MaybeSentinel
from libcst import Param
from libcst import RemovalSentinel

from ..config import Config
from ..consts import ANY
from ..to_camelcase import to_camelcase
from .transformer import Transformer


class PrototypeApplier(Transformer):
    def __init__(self, config: Config, annotations: dict[str, str]):
        super().__init__()
        self.config = config
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
        if to_camelcase(annotation) not in self.annotations:
            return updated_node
        if (
            self.annotations[to_camelcase(annotation)] != ANY
            or self.config.allow_any
        ):
            return updated_node.with_changes(
                annotation=libcst.parse_module(
                    f"def foo(bar: {self.annotations[
                        to_camelcase(annotation)].replace(
                        'collections.abc.', '')}):\n\tpass"
                )
                .body[0]
                .params.params[0]
                .annotation
            )
        return updated_node.with_changes(annotation=None)
