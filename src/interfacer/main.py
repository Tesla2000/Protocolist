from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from .add_inheritance import add_inheritance
from .config import Config
from .config import create_config_with_args
from .config import parse_arguments
from .transform.create_interfaces import create_interfaces


def main() -> int:
    args = parse_arguments(Config)
    config = create_config_with_args(Config, args)
    config.interfaces_path.write_text("")
    # fail = apply_pytype(config)
    fail = 0
    paths = tuple(
        filter(lambda path: path.suffix == ".py", map(Path, config.pos_args))
    )
    protocols = defaultdict(int)
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
    return fail
