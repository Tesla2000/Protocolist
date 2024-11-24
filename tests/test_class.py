from __future__ import annotations

from tests.class_inheritance import BaseFoo


class Foo(BaseFoo):
    def __init__(self, message):
        self.message = message
