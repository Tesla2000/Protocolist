from __future__ import annotations

import collections
import os
import typing
from pathlib import Path

import libcst as cst

from ..config import Config
from ..extract_annotations import extract_annotations
from ..protocol_markers.types_marker_factory import create_type_marker
from .class_extractor import ClassExtractor
from .class_extractor import GlobalClassExtractor
from .type_add_transformer import TypeAddTransformer


def create_protocols(
    filepath: Path,
    config: Config,
    protocols: dict,
    class_extractor: GlobalClassExtractor,
) -> tuple[int, Path]:
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
    annotations = extract_annotations(
        transformer.annotations, protocols, config
    )
    new_code = (
        "".join(
            set(
                f"from {config.interface_import_path} "
                f"import {annotation}\n"
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
                    f"from os import {annotation}\n"
                    for annotation in annotations
                    if annotation
                    in set(dir(os))
                    .difference(dir(typing))
                    .difference(dir(collections.abc))
                )
            )
            .union(
                set(
                    f"from {module_name} import {item_name}\n"
                    for item_name, module_name in external_imports.items()
                    if module_name not in ("typing", "collections.abc", "os")
                )
            )
        )
        + new_code
    ).replace("\t", config.tab_length * " ")
    if new_code != code:
        filepath.write_text(new_code)
        print(f"File {filepath} was modified")
        return 1, filepath
    return 0, filepath
