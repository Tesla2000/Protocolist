from __future__ import annotations

from typing import Optional

from libcst import Annotation
from libcst import Module
from libcst import Name
from libcst import Param
from libcst import Subscript
from libcst import SubscriptElement


def annotation2string(annotation: Optional[Annotation]) -> Optional[str]:
    if annotation is None:
        return
    return (
        Module([])
        .code_for_node(Param(name=Name("_"), annotation=annotation, star=""))
        .removeprefix("_: ")
    )


def subscript_element2string(substrip_element: SubscriptElement) -> str:
    value = substrip_element.slice.value
    if isinstance(value, Subscript):
        return f"{value.value.value}[{', '.join(
            map(subscript_element2string, value.slice)
        )}]"
    return value.value
