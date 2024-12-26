from __future__ import annotations

import os
from collections.abc import Iterable
from contextlib import contextmanager
from pathlib import Path

from protocolist.config import Config


@contextmanager
def transation(pos_args: Iterable[str], config: Config):
    paths = list(map(Path, pos_args)) + [config.interfaces_path]
    contents = tuple(path.read_text() for path in paths)
    origin_path = os.getcwd()
    os.chdir(config.project_root)
    try:
        yield
    except BaseException:
        print("Reverting changes please wait until process is done...")
        for path, content in zip(paths, contents):
            path.write_text(content)
        print("Changes reverted")
        raise
    finally:
        os.chdir(origin_path)
