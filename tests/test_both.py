from __future__ import annotations

from pathlib import Path

from protocolist.config import Config
from protocolist.presentation_option.presentation_option import (
    PresentationOption,
)
from protocolist.protocol_markers.mark_options import MarkOption

from tests.tests import Test


class TestPartial(Test):
    def test_partial(self):
        after = Path("tests/file_sets/set_1/both")
        config = Config(
            pos_args=tuple(
                map(
                    str,
                    self.before.iterdir(),
                )
            ),
            interfaces_path=str(self.protocols_path),
            mark_option=MarkOption.ALL,
            protocol_presentation=PresentationOption.BOTH,
        )
        self._test(after, config)
