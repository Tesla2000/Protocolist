from __future__ import annotations

from typing import Union

from tests.file_sets.char_sequence.before_update.protocols import Arg1
from tests.file_sets.char_sequence.before_update.protocols import CharSequence


def foo(arg: Union[Arg1, CharSequence]) -> None:
    return arg.startswith(arg)
