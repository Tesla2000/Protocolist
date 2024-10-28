from __future__ import annotations


def foo(message: Literal['message1']) -> None:
    message.some_method("str", "int", string="string")
    dictionary = {
        "role1": len(message.role),
        "role2": iter(message.role),
        "role3": message.role[0],
        "content": message.content.content,
    }
    for _ in message.content.content:
        pass
    print(len(message.content.content))
    del message.role[0]
    next(message.role)
    dictionary.get("role")
