from __future__ import annotations

from collections.abc import Mapping
from collections.abc import Sequence
from typing import Union

from tests.file_sets.set_1.before_update.protocols import Message2
from tests.file_sets.set_1.before_update.protocols import Message2FirstSubscript
from tests.file_sets.set_1.before_update.protocols import Message2SecondSubscript


def foo(message: Union[Mapping[Union[Message2FirstSubscript, str], Union[Message2SecondSubscript, Sequence]], Message2, Sequence[Union[Message2FirstSubscript, str]], memoryview]) -> None:
    for key in message:
        key.startswith("foo")
        message[key].count("foo")
