from __future__ import annotations

from typing import Sequence

import libcst as cst
from libcst import Module

from ..config import Config


class Transformer(cst.CSTTransformer):

    def __init__(self, module: Module, config: Config):
        super().__init__()
        self.config = config
        self.module = module

    def _get_path_attrs(self, elem, attrs: Sequence[str]):
        current_elem = elem
        for attr in attrs:
            if not hasattr(current_elem, attr):
                return
            current_elem = getattr(current_elem, attr)
        return current_elem

    def _set_path_attrs(self, elem, attrs: Sequence[str], **kwargs):
        inner_element = self._get_path_attrs(elem, attrs)
        inner_element = inner_element.with_changes(**kwargs)
        for i in range(1, len(attrs) + 1):
            outer_element = self._get_path_attrs(elem, attrs[:-i])
            inner_element = outer_element.with_changes(
                **{attrs[-i]: inner_element}
            )
        return inner_element
