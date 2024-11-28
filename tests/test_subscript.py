from __future__ import annotations


def foo(message) -> None:
    for key in message:
        key.starswith("foo")
        message[key].count("foo")
