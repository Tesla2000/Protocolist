from __future__ import annotations

import os
from pathlib import Path

import libcst as cst
from mypy.memprofile import defaultdict

from ..config import Config
from .type_add_transformer import TypeAddTransformer


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
                for annotation in transformer.annotations.values()
            )
        )
        + new_code
    )
    if new_code != code:
        filepath.write_text(new_code)
        print(f"File {filepath} was modified")
        return 1
    return 0
