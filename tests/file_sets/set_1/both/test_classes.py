from __future__ import annotations

from collections.abc import Collection
from collections.abc import Iterator
from typing import Union

from tests.file_sets.set_1.before_update.protocols import Content1
from tests.file_sets.set_1.before_update.protocols import Content2
from tests.file_sets.set_1.before_update.protocols import Message1
from tests.file_sets.set_1.before_update.protocols import Message2
from tests.file_sets.set_1.before_update.protocols import Message2FirstSubscript
from tests.file_sets.set_1.before_update.protocols import Message2SecondSubscript
from tests.file_sets.set_1.before_update.protocols import MessageFirstSubscript
from tests.file_sets.set_1.before_update.protocols import MessageSecondSubscript
from tests.file_sets.set_1.before_update.protocols import Role as Role_


class Content(str, Message2FirstSubscript, Message2SecondSubscript, MessageFirstSubscript, MessageSecondSubscript, Content2, Message2):
    content: Collection[str]


class Role(str, Message2FirstSubscript, Message2SecondSubscript, MessageFirstSubscript, Role_, MessageSecondSubscript, Content2, Message2):
    def __len__(self) -> int:
        return 1

    def __next__(self) -> "Role":
        return Role()

    def __getitem__(self, key) -> "Role":
        return Role()

    def __delitem__(self, key) -> None:
        return

    def __setitem__(self, key, value):
        return

    def __iter__(self) -> Iterator["Role"]:
        return (Role() for _ in range(3))


class MessageContent(Content1):
    string: str
    content: Content

    def __setitem__(self, key, value):
        return


class Message(Message1):
    def some_method(
        self, arg0: str, arg1: Union[int, str], string: Union[list, str]
    ) -> str:
        return arg0 + str(arg1) + str(string)

    role: Role
    content: MessageContent
