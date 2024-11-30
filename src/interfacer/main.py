from __future__ import annotations

import os
import re
from operator import itemgetter
from pathlib import Path

from .add_inheritance import add_inheritance
from .config import Config
from .config import create_config_with_args
from .config import parse_arguments
from .presentation_option.protocol_saver_factory import create_protocol_saver
from .protocol_dict import ProtocolDict
from .protocol_markers.types_marker_factory import create_type_marker
from .transaction import transation
from .transform.class_extractor import ClassExtractor
from .transform.class_extractor import GlobalClassExtractor
from .transform.create_protocols import create_protocols


def main() -> int:
    args = parse_arguments(Config)
    config = create_config_with_args(Config, args)
    with transation(config.pos_args, config.interfaces_path):
        return _main(config)


def _main(config: Config) -> int:
    fail = 0
    paths = tuple(
        filter(lambda path: path.suffix == ".py", map(Path, config.pos_args))
    )
    # fail = apply_pytype(config)
    global_class_extractor = GlobalClassExtractor(config)
    classes = ClassExtractor(
        config, create_type_marker(config)
    ).extract_classes(config.interfaces_path.read_text())
    interfaces = dict(
        sorted(
            (
                (item[0][0], int(item[0][1]))
                for item in map(
                    lambda name: re.findall(r"(\D+)(\d+)", name),
                    classes.keys(),
                )
                if item
            ),
            key=itemgetter(1),
        )
    )
    protocols = ProtocolDict(int, **interfaces)
    for filepath in paths:
        fail |= create_protocols(
            filepath,
            config=config,
            protocols=protocols,
            class_extractor=global_class_extractor,
        )
    create_protocol_saver(config).modify_protocols()
    for filepath in paths:
        fail |= add_inheritance(
            filepath, config=config, class_extractor=global_class_extractor
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
