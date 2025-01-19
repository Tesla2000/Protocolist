from __future__ import annotations

import os
import time
from itertools import filterfalse
from pathlib import Path

from protocolist.config import Config
from protocolist.main import protocol
from protocolist.presentation_option.presentation_option import (
    PresentationOption,
)
from protocolist.protocol_markers.mark_options import MarkOption
from protocolist.transform.class_extractor import ClassExtractor

from tests.test import Test


class TestCombinedMultiprocess(Test):
    def test_combined(self):
        after = Path("tests/file_sets/general_set/combined")
        start = time.time()
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
            n_workers=4,
        )
        before_update_files = tuple(
            (filepath, filepath.read_text())
            for filepath in self.before.iterdir()
        )
        try:
            protocol(config)
            self.assertEqual(
                len(
                    ClassExtractor(config).extract_protocols(
                        self.protocols_path.read_text()
                    )
                ),
                len(
                    ClassExtractor(config).extract_protocols(
                        (after / self.protocol_file_name).read_text()
                    )
                ),
            )

        finally:
            tuple(
                filepath.write_text(content)
                for filepath, content in before_update_files
            )
            if self.protocols_path.exists():
                os.remove(self.protocols_path)
        self.assertGreater(30.0, time.time() - start)
