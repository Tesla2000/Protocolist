from __future__ import annotations

from collections.abc import Collection
from collections.abc import Iterator
from typing import Any
from typing import Union


class Content(str):
    content: Collection


class Role(str):
    def __len__(self) -> int:
        return 1

    def __next__(self) -> "Role":
        return Role()

    def __getitem__(self, key: Any) -> "Role":
        return Role()

    def __delitem__(self, key: Any) -> None:
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
