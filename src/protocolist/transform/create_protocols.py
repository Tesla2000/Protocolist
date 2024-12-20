from __future__ import annotations

import collections
import typing
from itertools import chain
from itertools import filterfalse
from operator import itemgetter
from pathlib import Path

import libcst as cst
from mypy.memprofile import defaultdict

from ..config import Config
from ..consts import builtin_types
from ..protocol_markers.types_marker_factory import create_type_marker
from ..utils.split_annotations import split_annotations
from .class_extractor import ClassExtractor
from .class_extractor import GlobalClassExtractor
from .type_add_transformer import TypeAddTransformer


def create_protocols(
    filepath: Path,
    config: Config,
    protocols: defaultdict[int],
    class_extractor: GlobalClassExtractor,
) -> int:
    code = filepath.read_text()
    module = cst.parse_module(code)
    transformer = TypeAddTransformer(
        config,
        protocols,
        create_type_marker(config),
        class_extractor,
        filepath,
    )
    new_code = module.visit(transformer).code
    assert len(transformer.imports) == len(
        dict(transformer.imports)
    ), "We don't support that yet. Contact Protocolist creator please"
    external_imports = dict(transformer.imports)
    protocols = ClassExtractor(
        config, create_type_marker(config)
    ).extract_protocols(config.interfaces_path.read_text())
    annotations = tuple(
        annotation
        for annotation in filterfalse(
            tuple(map(itemgetter(0), builtin_types)).__contains__,
            chain.from_iterable(
                map(
                    split_annotations,
                    transformer.annotations.values(),
                )
            ),
        )
        if (
            annotation in protocols
            or annotation in dir(typing)
            or annotation in dir(collections.abc)
        )
    )
    new_code = (
        "".join(
            set(
                f"from {config.interface_import_path} import {annotation}\n"
                for annotation in annotations
                if annotation in protocols
            )
            .union(
                set(
                    f"from typing import {annotation}\n"
                    for annotation in annotations
                    if annotation in dir(typing)
                )
            )
            .union(
                set(
                    f"from collections.abc import {annotation}\n"
                    for annotation in annotations
                    if annotation in dir(collections.abc)
                )
            )
            .union(
                set(
                    f"from {module_name} import {item_name}\n"
                    for item_name, module_name in external_imports.items()
                    if module_name not in ("typing", "collections.abc")
                )
            )
        )
        + new_code
    ).replace("\t", config.tab_length * " ")
    if new_code != code:
        filepath.write_text(new_code)
        print(f"File {filepath} was modified")
        return 1
    return 0
