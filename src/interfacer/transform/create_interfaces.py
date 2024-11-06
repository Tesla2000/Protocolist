from __future__ import annotations

import os
from itertools import chain
from pathlib import Path

import libcst as cst
from mypy.memprofile import defaultdict

from .type_add_transformer import TypeAddTransformer
from ..config import Config
from ..consts import ANY
from ..protocol_markers.types_marker_factory import create_type_marker


def create_interfaces(
    filepath: Path, config: Config, protocols: defaultdict[int]
) -> int:
    code = filepath.read_text()
    module = cst.parse_module(code)
    transformer = TypeAddTransformer(config, protocols, create_type_marker(config))
    new_code = module.visit(transformer).code
    new_code = (
        "".join(
            set(
                f"from {config.interface_import_path} import {annotation}\n"
                for annotation in chain.from_iterable(map(_split_annotations, transformer.annotations.values()))
                if annotation != ANY or config.allow_any
            )
        )
        + new_code
    )
    if new_code != code:
        filepath.write_text(new_code)
        print(f"File {filepath} was modified")
        return 1
    return 0

def _split_annotations(annotation: str) -> list[str]:
    if not annotation.startswith("Union["):
        return [annotation]
    return list(annotation.strip().replace("collections.abc.", "") for annotation in annotation.replace("Union[", "").strip("]").split(",")) + ["Union"]