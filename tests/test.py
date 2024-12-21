from __future__ import annotations

from pathlib import Path

from tests.test_base import TestBase


class Test(TestBase):
    def setUp(self):
        self.before = Path("tests/file_sets/set_1/before_update")
        super().setUp()