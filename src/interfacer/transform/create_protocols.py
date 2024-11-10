from __future__ import annotations

import traceback
from itertools import chain
from pathlib import Path

import libcst as cst
from mypy.memprofile import defaultdict

from ..config import Config
from ..consts import ANY
from ..protocol_markers.types_marker_factory import create_type_marker
from .type_add_transformer import TypeAddTransformer


def create_protocols(
    filepath: Path, config: Config, protocols: defaultdict[int]
) -> int:
    code = filepath.read_text()
    module = cst.parse_module(code)
    transformer = TypeAddTransformer(
        config, protocols, create_type_marker(config)
    )
    try:
        new_code = module.visit(transformer).code
    except Exception:
        traceback.print_exc()
        raise
    assert len(transformer.imports) == len(
        dict(transformer.imports)
    ), "We don't support that yet. Contact Protocolist creator please"
    external_imports = dict(transformer.imports)
    new_code = (
        "".join(
            set(
                f"from {config.interface_import_path} import {annotation}\n"
                for annotation in chain.from_iterable(
                    map(_split_annotations, transformer.annotations.values())
                )
                if (annotation != ANY or config.allow_any)
                and annotation not in external_imports
            ).union(
                set(
                    f"from {module_name} import {item_name}\n"
                    for item_name, module_name in external_imports.items()
                )
            )
        )
        + new_code
    )
    if new_code != code:
        filepath.write_text(new_code)
        print(f"File {filepath} was modified")
        return 1
    return 0


def _split_annotations(annotation: str) -> list[str]:
    if not annotation.startswith("Union["):
        return [annotation]
    return list(
        annotation.strip().replace("collections.abc.", "")
        for annotation in annotation.replace("Union[", "")
        .strip("]")
        .split(",")
    ) + ["Union"]
