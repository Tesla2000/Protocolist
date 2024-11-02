from __future__ import annotations

from collections.abc import Iterator
from typing import Collection
from typing import Union

from interfaces.interfaces import Any


class Content:
    content: Collection


class Role:
    def __len__(self) -> int:
        return 1

    def __next__(self) -> "Role":
        return Role()

    def __getitem__(self, key: Any) -> "Role":
        return Role()

    def __delitem__(self, key: Any) -> None:
        return

    def __iter__(self) -> Iterator["Role"]:
        return (Role() for _ in range(3))


class Message:
    def some_method(
        self, arg0: str, arg1: Union[int, str], string: Union[list, str]
    ) -> str:
        return arg0 + str(arg1) + str(string)

    role: Role
    content: Content
