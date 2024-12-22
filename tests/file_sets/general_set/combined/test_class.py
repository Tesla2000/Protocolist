from __future__ import annotations

from tests.file_sets.general_set.before_update.class_inheritance import BaseFoo
from tests.file_sets.general_set.before_update.protocols import Message


class Foo(BaseFoo):
    def __init__(self, message: Message):
        self.message = message
