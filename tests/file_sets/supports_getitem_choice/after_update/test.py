from __future__ import annotations

from collections.abc import Sequence


def foo(array: Sequence[Sequence[Sequence[str]]]) -> bool:
    return array[0][0][0].startswith("a")
