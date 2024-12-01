from __future__ import annotations

import os
import re
import shutil
from pathlib import Path

from .config import Config
from .convert_relative_to_absolute import convert_relative_to_absolute


def apply_pytype(config: Config) -> int:
    fail = 0
    root = Path(os.getcwd())
    pyi_root = Path(".pytype/pyi")
    os.system(
        f"pytype {' '.join(config.pos_args)} --no-report-errors "
        f"--use-fiddle-overlay --no-return-any --precise-return "
        f"--bind-decorated-methods"
    )
    modified_file_paths = tuple(
        Path(path).absolute() for path in config.pos_args
    )
    for dirpath, dirnames, filenames in os.walk(pyi_root):
        for filename in filenames:
            pyi_file = Path(dirpath).joinpath(filename)
            relative_path = pyi_file.relative_to(pyi_root)
            py_file = root.joinpath(relative_path).with_suffix(".py")
            if py_file.absolute() not in modified_file_paths:
                continue
            previous = py_file.read_text()
            os.system(f"merge-pyi -i {py_file} {pyi_file}")
            now = py_file.read_text()
            if previous != now:
                relative_imports = re.findall(
                    r"(from \.\S+ import \(\s+[^\n]+\s+\)|"
                    r"from \.\S+ import [^\n]+|import \.[^\n]+)",
                    previous,
                )
                absolute_imports = convert_relative_to_absolute(
                    relative_imports, relative_path
                )
                for absolute_import in absolute_imports:
                    now = now.replace(absolute_import + "\n", "", 1)
                py_file.write_text(now)
                fail |= now != previous
    shutil.rmtree(".pytype")
    return fail
