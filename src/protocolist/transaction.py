from __future__ import annotations

from collections.abc import Iterable
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def transation(pos_args: Iterable[str], interface_path: Path):
    paths = list(map(Path, pos_args)) + [interface_path]
    contents = tuple(path.read_text() for path in paths)
    try:
        yield
    except BaseException:
        for path, content in zip(paths, contents):
            path.write_text(content)
        raise
