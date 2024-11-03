from __future__ import annotations

import os
from itertools import chain
from pathlib import Path

import libcst as cst
from mypy.memprofile import defaultdict

from ..config import Config
from .type_add_transformer import TypeAddTransformer
from ..consts import ANY


def create_interfaces(
    filepath: Path, config: Config, protocols: defaultdict[int]
) -> int:
    code = filepath.read_text()
    module = cst.parse_module(code)
    transformer = TypeAddTransformer(config, protocols)
    new_code = module.visit(transformer).code
    interface_path = ".".join(
        config.interfaces_path.relative_to(os.getcwd()).with_suffix("").parts
    )
    new_code = (
        "".join(
            set(
                f"from {interface_path} import {annotation}\n"
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
