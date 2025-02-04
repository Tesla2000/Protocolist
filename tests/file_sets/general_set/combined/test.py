from __future__ import annotations

from tests.file_sets.general_set.before_update.protocols import Message


def foo(message: Message) -> None:
    message.some_method("str", "int", string="string")
    message.some_method("str", 5, string=[])
    dictionary = {
        "role1": len(message.role),
        "role2": iter(message.role),
        "role3": message.role[0],
        "content": message.content.content,
    }
    message.role[1] = "foo"
    assert message.content.string.startswith("a")
    for string in message.content.content:
        string.startswith("foo")
    print(len(message.content.content))
    del message.role[0]
    next(message.role)
    dictionary.get("role")
