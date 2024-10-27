from __future__ import annotations

import re
from pathlib import Path


def convert_relative_to_absolute(import_lines, file_path: Path):
    def convert_line(line):
        import_path = file_path
        start_word = line.split()[0]
        for dot in re.findall(r"\.+", line)[0]:
            import_path = import_path.parent
        absolute_import = (
            start_word
            + " "
            + ".".join(import_path.parts)
            + "."
            + re.findall(r"\.+(\S+)", line)[0]
        )
        if start_word == "from":
            return (
                absolute_import + " import " + line.partition(" import ")[-1]
            )
        return absolute_import

    def reformat(line: str) -> str:
        return re.sub(r"[\s()]+", " ", line).rstrip(" ,")

    return list(map(reformat, map(convert_line, import_lines)))
