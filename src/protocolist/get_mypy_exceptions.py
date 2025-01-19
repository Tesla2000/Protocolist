from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

import mypy.api


def get_mypy_exceptions(
    mypy_folder: Path, updated_code: str, strict: bool = True
) -> list[str]:
    file_path = mypy_folder.joinpath(str(uuid4())).with_suffix(".py")
    file_path.write_text(updated_code)
    result = mypy.api.run([str(file_path)] + ["--strict"] if strict else [])[
        0
    ].splitlines()[:-1]
    os.remove(file_path)
    return result
