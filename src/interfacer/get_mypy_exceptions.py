from __future__ import annotations

from pathlib import Path

import mypy.api


def get_mypy_exceptions(
    temp_python_file: Path, updated_code: str, strict: bool = True
) -> list[str]:
    temp_python_file.write_text(updated_code)
    return mypy.api.run(
        [str(temp_python_file)] + ["--strict"] if strict else []
    )[0].splitlines()[:-1]
