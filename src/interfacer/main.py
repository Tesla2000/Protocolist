from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from .apply_pytype import apply_pytype
from .config import Config
from .config import create_config_with_args
from .config import parse_arguments
from .transform.modify_file import modify_file


def main() -> int:
    args = parse_arguments(Config)
    config = create_config_with_args(Config, args)
    fail = apply_pytype(config)
    paths = map(Path, config.pos_args)
    protocols = defaultdict(int)
    for filepath in filter(lambda path: path.suffix == ".py", paths):
        fail |= modify_file(
            filepath,
            config=config,
            protocols=protocols,
        )
    # structure_interfaces(config)
    return fail
