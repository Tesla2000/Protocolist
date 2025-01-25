from __future__ import annotations

import re
from collections.abc import Iterable
from collections.abc import Sequence


def filter_mypy_by_lines(
    lines: Iterable[str], start_line: int, end_line: int
) -> Sequence[str]:
    return tuple(
        line
        for line in lines
        if start_line
        <= int(re.findall(r"\d+", line.split()[0])[-1])
        <= end_line
    )
