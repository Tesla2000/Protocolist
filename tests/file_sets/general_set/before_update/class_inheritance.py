from __future__ import annotations

from typing import Any


class BaseBaseFoo:
    def foo(self) -> None:
        self.message.some_method("str", "int", string="string")
        self.message.some_method("str", 5, string=[])
        dictionary = {
            "role1": len(self.message.role),
            "role2": iter(self.message.role),
            "role3": self.message.role[0],
            "content": self.message.content.content,
        }
        self.message.role[1] = "foo"
        assert self.message.content.string.startswith("a")
        for string in self.message.content.content:
            string.startswith("foo")
        print(len(self.message.content.content))
        del self.message.role[0]
        next(self.message.role)
        dictionary.get("role")


class M:
    m: Any

    def foo(self) -> None:
        pass


class BaseFoo(BaseBaseFoo, M):
    pass
