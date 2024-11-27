from __future__ import annotations

import collections
import traceback
import typing
from itertools import chain
from itertools import filterfalse
from operator import itemgetter
from pathlib import Path
from typing import Optional

import libcst
import libcst as cst
from libcst import Name
from mypy.memprofile import defaultdict

from ..config import Config
from ..consts import ANY
from ..consts import builtin_types
from ..protocol_markers.types_marker_factory import create_type_marker
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
        config, protocols, create_type_marker(config), class_extractor
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
    protocols = ClassExtractor(create_type_marker(config)).extract_protocols(
        config.interfaces_path.read_text()
    )
    annotations = tuple(
        annotation
        for annotation in filterfalse(
            tuple(map(itemgetter(0), builtin_types)).__contains__,
            chain.from_iterable(
                map(
                    _split_annotations,
                    transformer.annotations.values(),
                )
            ),
        )
        if (annotation != ANY or config.allow_any)
        and (
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
    # if not annotation.startswith("Union["):
    #     return [annotation]
    names_getter = _NamesGetter()
    libcst.parse_expression(annotation).visit(names_getter)
    return names_getter.names
    # return list(
    #     annotation.strip().replace("collections.abc.", "")
    #     for annotation in annotation.replace("Union[", "")
    #     .removesuffix("]")
    #     .split(",")
    # ) + ["Union"]


class _NamesGetter(libcst.CSTTransformer):
    def __init__(self):
        super().__init__()
        self.names = []

    def visit_Name(self, node: "Name") -> Optional[bool]:
        self.names.append(node.value)
        return super().visit_Name(node)
