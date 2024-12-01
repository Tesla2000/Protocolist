from __future__ import annotations

import os
from pathlib import Path


def filepath2import_path(filepath: Path) -> str:
    return ".".join(
        filepath.absolute().relative_to(os.getcwd()).with_suffix("").parts
    )
