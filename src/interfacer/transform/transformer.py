from __future__ import annotations

from collections.abc import Sequence

import libcst as cst


class Transformer(cst.CSTTransformer):
    def _get_path_attrs(self, elem, attrs: Sequence[str]):
        current_elem = elem
        for attr in attrs:
            if isinstance(attr, int):
                if len(current_elem) <= attr:
                    return
                current_elem = current_elem[attr]
            else:
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
