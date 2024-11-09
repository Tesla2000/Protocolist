from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterable


@contextmanager
def transation(pos_args: Iterable[str]):
    paths = tuple(map(Path, pos_args))
    contents = tuple(path.read_text() for path in paths)
    try:
        yield
    except BaseException:
        for path, content in zip(paths, contents):
            path.write_text(content)
