from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import Path

from more_itertools.more import always_iterable


def convert_relative_to_absolute(import_lines: Iterable[str], file_path: Path):
    def convert_line(line: str):
        import_str_path = line.split()[1]
        absolute_path = convert_relative_path(file_path, import_str_path)
        start_word = line.split()[0]
        absolute_import = start_word + " " + absolute_path
        if start_word == "from":
            return (
                absolute_import + " import " + line.partition(" import ")[-1]
            )
        return absolute_import

    def reformat(line: str) -> str:
        return re.sub(r"[\s()]+", " ", line).rstrip(" ,")

    return list(
        map(reformat, map(convert_line, always_iterable(import_lines)))
    )


def convert_relative_path(file_path: Path, import_str_path: str) -> str:
    if not import_str_path.startswith("."):
        return import_str_path
    import_path = file_path
    for dot in re.findall(r"\.+", import_str_path)[0]:
        import_path = import_path.parent
    return ".".join(
        (*import_path.parts, re.findall(r"\.+(\S+)", import_str_path)[0])
    )
