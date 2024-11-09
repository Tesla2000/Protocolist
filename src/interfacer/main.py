from __future__ import annotations

import os
from pathlib import Path

from .add_inheritance import add_inheritance
from .config import Config
from .config import create_config_with_args
from .config import parse_arguments
from .ProtocolDict import ProtocolDict
from .transaction import transation
from .transform.create_interfaces import create_interfaces


def main() -> int:
    args = parse_arguments(Config)
    config = create_config_with_args(Config, args)
    with transation(config.pos_args):
        return _main(config)


def _main(config: Config) -> int:
    config.interfaces_path.write_text("")
    # fail = apply_pytype(config)
    fail = 0
    paths = tuple(
        filter(lambda path: path.suffix == ".py", map(Path, config.pos_args))
    )
    protocols = ProtocolDict(int)
    for filepath in paths:
        fail |= create_interfaces(
            filepath,
            config=config,
            protocols=protocols,
        )
    for filepath in paths:
        fail |= add_inheritance(
            filepath,
            config=config,
        )
    fail |= os.system(
        f"reorder-python-imports {' '.join(config.pos_args)} "
        f"{config.interfaces_path.absolute()}"
    )
    fail |= os.system(
        f"autoflake --in-place --remove-all-unused-imports "
        f"{' '.join(config.pos_args)} {config.interfaces_path.absolute()}"
    )
    return fail
