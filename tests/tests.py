from __future__ import annotations

import os
from pathlib import Path
from unittest import TestCase

from protocolist.config import Config
from protocolist.main import protocol
from protocolist.presentation_option.presentation_option import (
    PresentationOption,
)
from protocolist.protocol_markers.mark_options import MarkOption


class TestCombined(TestCase):
    def setUp(self):
        self.before = Path("tests/file_sets/set_1/before_update")
        self.protocols_path = self.before / "protocols.py"

    def test_combined(self):
        after = Path("tests/file_sets/set_1/combined")
        config = Config(
            pos_args=tuple(
                map(
                    str,
                    self.before.iterdir(),
                )
            ),
            interfaces_path=str(self.protocols_path),
            mark_option=MarkOption.ALL,
            protocol_presentation=PresentationOption.COMBINED_PROTOCOLS,
        )
        self._test(after, config)

    def _test(self, after: Path, config: Config):
        before_update_files = tuple(
            (filepath, filepath.read_text())
            for filepath in self.before.iterdir()
        )
        after_update_files = tuple(
            (filepath, filepath.read_text()) for filepath in after.iterdir()
        )
        try:
            protocol(config)
            self.assertEqual(
                tuple(
                    (filepath.name, content)
                    for filepath, content in after_update_files
                ),
                tuple(
                    (filepath.name, filepath.read_text())
                    for filepath in self.before.iterdir()
                ),
            )
        finally:
            tuple(
                filepath.write_text(content)
                for filepath, content in before_update_files
            )
            if self.protocols_path.exists():
                os.remove(self.protocols_path)
