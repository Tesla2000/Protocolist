from __future__ import annotations

from typing import Union

from tests.file_sets.recursive_type.before_update.protocols import Arg1


def foo1(arg: Union[Arg1, str]) -> bool:
    return arg.startswith("a")
