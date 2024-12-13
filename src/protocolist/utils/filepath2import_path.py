from __future__ import annotations

import os
from pathlib import Path


def filepath2import_path(
    filepath: Path, project_root: Path | str = os.getcwd()
) -> str:
    return ".".join(
        filepath.absolute().relative_to(project_root).with_suffix("").parts
    )
