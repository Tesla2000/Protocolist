from __future__ import annotations

from pathlib import Path

from protocolist.config import Config
from protocolist.presentation_option.presentation_option import (
    PresentationOption,
)
from protocolist.protocol_markers.mark_options import MarkOption

from tests.test_base import TestBase


class TestMath(TestBase):
    def setUp(self):
        self.base = Path("tests/file_sets/math")
        self.before = self.base / Path("before_update")
        super().setUp()

    def test(self):
        after = self.base / Path("after_update")
        config = Config(
            pos_args=tuple(
                map(
                    str,
                    self.before.iterdir(),
                )
            ),
            interfaces_path=str(self.protocols_path),
            add_protocols_on_builtin=True,
            mark_option=MarkOption.ALL,
            protocol_presentation=PresentationOption.PARTIAL_PROTOCOLS,
        )
        self._test(after, config)
