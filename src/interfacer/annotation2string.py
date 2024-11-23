from __future__ import annotations

from typing import Optional

from libcst import Annotation
from libcst import SubscriptElement


def annotation2string(annotation: Optional[Annotation]) -> Optional[str]:
    if annotation is None:
        return
    if isinstance(annotation.annotation.value, str):
        return annotation.annotation.value
    return f"Union[{', '.join(
        map(subscript_element2string, annotation.annotation.slice)
    )}]"


def subscript_element2string(substrip_element: SubscriptElement) -> str:
    return substrip_element.slice.value.value
