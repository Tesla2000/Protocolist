from __future__ import annotations

import os
from pathlib import Path


def import2path(import_string: str) -> Path:
    return (
        Path(os.getcwd())
        .joinpath(*import_string.split("."))
        .with_suffix(".py")
    )
