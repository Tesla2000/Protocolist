from __future__ import annotations

from collections.abc import Mapping
from collections.abc import Sequence
from typing import Union

from tests.file_sets.set_1.before_update.protocols import Message
from tests.file_sets.set_1.before_update.protocols import MessageFirstSubscript
from tests.file_sets.set_1.before_update.protocols import MessageSecondSubscript


def foo(message: Union[Mapping[Union[MessageFirstSubscript, str], Union[MessageSecondSubscript, Sequence]], Message, Sequence[Union[MessageFirstSubscript, str]], memoryview]) -> None:
    for key in message:
        key.startswith("foo")
        message[key].count("foo")
