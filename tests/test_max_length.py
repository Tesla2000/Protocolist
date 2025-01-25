from __future__ import annotations

from pathlib import Path

from protocolist.config import Config
from protocolist.presentation_option.presentation_option import (
    PresentationOption,
)
from protocolist.protocol_markers.mark_options import MarkOption

from tests.test_base import TestBase


class TestSupportsIndex(TestBase):
    def setUp(self):
        self.before = Path(
            "tests/file_sets/supports_index_limit/before_update"
        )
        super().setUp()

    def test(self):
        after = Path("tests/file_sets/supports_index_limit/after_update")
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
            max_hint_length=100,
        )
        self._test(after, config)
