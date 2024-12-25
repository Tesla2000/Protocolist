from __future__ import annotations

from tests.file_sets.recursive_type.before_update.imported import foo1


def foo2(arg) -> bool:
    return foo1(arg)


def foo3(arg) -> bool:
    return foo2(arg)
