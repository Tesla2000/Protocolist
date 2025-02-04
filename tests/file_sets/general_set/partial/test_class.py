from __future__ import annotations

from tests.file_sets.general_set.before_update.class_inheritance import BaseFoo
from tests.file_sets.general_set.before_update.protocols import Message1


class Foo(BaseFoo):
    def __init__(self, message: Message1):
        self.message = message
