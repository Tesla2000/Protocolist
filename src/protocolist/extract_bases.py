from __future__ import annotations

from collections.abc import Iterable

from libcst import ClassDef
from more_itertools import map_except


def extract_bases(node: ClassDef) -> Iterable[str]:
    return filter(
        str.__instancecheck__,
        map_except(lambda base: base.value.value, node.bases, AttributeError),
    )
