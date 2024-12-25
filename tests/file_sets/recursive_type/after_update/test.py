from __future__ import annotations

from typing import Union

from tests.file_sets.recursive_type.before_update.imported import foo1
from tests.file_sets.recursive_type.before_update.protocols import Arg1


def foo2(arg: Union[Arg1, str]) -> bool:
    return foo1(arg)


def foo3(arg: Union[Arg1, str]) -> bool:
    return foo2(arg)
