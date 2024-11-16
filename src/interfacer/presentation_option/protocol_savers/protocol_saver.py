from __future__ import annotations

import re
import sys
from abc import ABC
from abc import abstractmethod
from operator import itemgetter
from pathlib import Path

import libcst
from more_itertools.more import map_reduce

from ...config import Config
from ...protocol_markers.types_marker_factory import create_type_marker
from ...transform.class_extractor import ClassExtractor
from ..presentation_option import PresentationOption
from ..replace_partial_with_combined import ReplaceImportsAndNames


class ProtocolSaver(ABC):
    type: PresentationOption
    replace_dictionary: dict[str, str]

    def __init__(self, config: Config):
        self.config = config

    def modify_protocols(self) -> None:
        self._deduplicate()
        self._modify_protocols()
        self._update_imports_and_names()

    @abstractmethod
    def _modify_protocols(self) -> None:
        pass

    def _deduplicate(self):
        extractor = ClassExtractor(create_type_marker(self.config))
        code = self.config.interfaces_path.read_text()
        extracted_classes = extractor.extract_classes(code)
        grouped_classes = map_reduce(
            extracted_classes.items(),
            lambda item: item[1].partition("(Protocol):\n")[-1],
        )
        unique_classes = dict(
            sorted(
                items,
                key=lambda item: int(
                    (re.findall(r"\d+", item[0]) or [sys.maxsize])[0]
                ),
            )[0]
            for items in grouped_classes.values()
        )
        self.replace_dictionary = {
            name: next(
                filter(unique_classes.__contains__, map(itemgetter(0), names))
            )
            for names in grouped_classes.values()
            for name, _ in names
        }
        imports = code.partition("@")[0]
        self.config.interfaces_path.write_text(
            imports + "".join(unique_classes.values())
        )

    def _update_imports_and_names(self):
        for filepath in filter(
            lambda path: path.suffix == ".py", map(Path, self.config.pos_args)
        ):
            filepath.write_text(
                libcst.parse_module(filepath.read_text())
                .visit(
                    ReplaceImportsAndNames(
                        self.config, self.replace_dictionary
                    )
                )
                .code
            )
