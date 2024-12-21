from __future__ import annotations

from itertools import filterfalse
from pathlib import Path

from protocolist.config import Config
from protocolist.presentation_option.presentation_option import (
    PresentationOption,
)
from protocolist.protocol_markers.mark_options import MarkOption

from tests.test import Test


class TestCombined(Test):
    def test_combined(self):
        after = Path("tests/file_sets/set_1/combined")
        config = Config(
            pos_args=tuple(
                filterfalse(
                    str(self.protocols_path).__eq__,
                    map(
                        str,
                        self.before.iterdir(),
                    ),
                )
            ),
            interfaces_path=str(self.protocols_path),
            mark_option=MarkOption.ALL,
            protocol_presentation=PresentationOption.COMBINED_PROTOCOLS,
        )
        self._test(after, config)
