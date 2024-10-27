from __future__ import annotations

from pathlib import Path

import libcst as cst

from ..config import Config
from .type_add_transformer import TypeAddTransformer


def modify_file(filepath: Path, config: Config) -> int:
    code = filepath.read_text()
    module = cst.parse_module(code)
    transformer = TypeAddTransformer(module, config)
    new_code = module.visit(transformer).code
    if new_code != code:
        filepath.write_text(new_code)
        print(f"File {filepath} was modified")
        return 1
    return 0
