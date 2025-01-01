from __future__ import annotations

import os
import re
from itertools import compress
from operator import itemgetter
from pathlib import Path

from .add_inheritance import add_inheritance
from .config import Config
from .config import create_config_with_args
from .config import parse_arguments
from .presentation_option.protocol_saver_factory import create_protocol_saver
from .protocol_dict import ProtocolDict
from .protocol_markers.types_marker_factory import create_type_marker
from .remove_star_imports import remove_star_imports
from .sort_files_by_import_order import sort_files_by_import_order
from .transaction import transation
from .transform.class_extractor import ClassExtractor
from .transform.class_extractor import GlobalClassExtractor
from .transform.create_protocols import create_protocols


def main() -> int:
    args = parse_arguments(Config)
    config = create_config_with_args(Config, args)
    with transation(config.pos_args, config):
        return protocol(config)


def protocol(config: Config) -> int:
    paths = tuple(
        filter(lambda path: path.suffix == ".py", map(Path, config.pos_args))
    )
    global_class_extractor = GlobalClassExtractor(config)
    paths = sort_files_by_import_order(paths, global_class_extractor)
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
    is_file_modified = tuple(
        create_protocols(
            filepath,
            config=config,
            protocols=protocols,
            class_extractor=global_class_extractor,
        )
        for filepath in paths
    )
    create_protocol_saver(config).modify_protocols()
    is_file_modified = tuple(
        add_inheritance(
            filepath, config=config, class_extractor=global_class_extractor
        )
        or modified
        for filepath, modified in zip(paths, is_file_modified)
    )
    remove_star_imports(config)
    fail = any(is_file_modified)
    str_path = " ".join(
        f'"{path}"' for path in compress(config.pos_args, is_file_modified)
    )
    fail |= os.system(
        f"autoflake --in-place --remove-all-unused-imports "
        f"{str_path} {config.interfaces_path.absolute()}"
    )
    fail |= os.system(
        f"reorder-python-imports "
        f"{str_path} {config.interfaces_path.absolute()} --py39-plus"
    )
    return fail
