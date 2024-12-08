from __future__ import annotations

from tests.file_sets.set_1.before_update.class_inheritance import BaseFoo
from tests.file_sets.set_1.before_update.protocols import Message


class Foo(BaseFoo):
    def __init__(self, message: Message):
        self.message = message
