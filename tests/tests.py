from __future__ import annotations

import os
from pathlib import Path
from unittest import TestCase

from protocolist.config import Config
from protocolist.main import protocol
from protocolist.transform.class_extractor import ClassExtractor


class Test(TestCase):
    def setUp(self):
        self.protocol_file_name = "protocols.py"
        self.before = Path("tests/file_sets/set_1/before_update")
        self.protocol_file_name = "protocols.py"
        self.protocols_path = self.before / self.protocol_file_name

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
                    if filepath.name != self.protocols_path.name
                ),
                tuple(
                    (filepath.name, filepath.read_text())
                    for filepath in self.before.iterdir()
                    if filepath != self.protocols_path
                ),
            )
            self.assertEqual(
                ClassExtractor(config).extract_protocols(
                    self.protocols_path.read_text()
                ),
                ClassExtractor(config).extract_protocols(
                    (after / self.protocol_file_name).read_text()
                ),
            )
            protocol(config)
            self.assertEqual(
                tuple(
                    (filepath.name, content)
                    for filepath, content in after_update_files
                    if filepath.name != self.protocols_path.name
                ),
                tuple(
                    (filepath.name, filepath.read_text())
                    for filepath in self.before.iterdir()
                    if filepath != self.protocols_path
                ),
            )
            self.assertEqual(
                ClassExtractor(config).extract_protocols(
                    self.protocols_path.read_text()
                ),
                ClassExtractor(config).extract_protocols(
                    (after / self.protocol_file_name).read_text()
                ),
            )
        finally:
            tuple(
                filepath.write_text(content)
                for filepath, content in before_update_files
            )
            if self.protocols_path.exists():
                os.remove(self.protocols_path)
