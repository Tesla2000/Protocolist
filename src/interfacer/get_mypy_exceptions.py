from __future__ import annotations

from pathlib import Path

import mypy.api


def get_mypy_exceptions(
    temp_python_file: Path, updated_code: str
) -> list[str]:
    temp_python_file.write_text(updated_code)
    return mypy.api.run([str(temp_python_file), "--strict"])[0].splitlines()[
        :-1
    ]
