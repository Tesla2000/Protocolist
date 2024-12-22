from __future__ import annotations

from collections.abc import Collection
from collections.abc import Iterator
from typing import Union

from tests.file_sets.general_set.before_update.protocols import ContentSubscript
from tests.file_sets.general_set.before_update.protocols import MessageSecondSubscript
from tests.file_sets.general_set.before_update.protocols import Role as Role_


class Content(str, ContentSubscript, MessageSecondSubscript):
    content: Collection[str]


class Role(str, ContentSubscript, MessageSecondSubscript, Role_):
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


class MessageContent:
    string: str
    content: Content

    def __setitem__(self, key, value):
        return


class Message:
    def some_method(
        self, arg0: str, arg1: Union[int, str], string: Union[list, str]
    ) -> str:
        return arg0 + str(arg1) + str(string)

    role: Role
    content: MessageContent
