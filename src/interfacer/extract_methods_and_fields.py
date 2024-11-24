from __future__ import annotations

import re
from pathlib import Path

from .consts import abc_classes
from .consts import builtin_types
from .import2path import import2path
from .transform.class_extractor import GlobalClassExtractor


def extract_methods_and_fields(code: str) -> tuple[set[str], set[str]]:
    return set(re.findall(r"    def [^\(]+\([^\)]+\)[^:]*:", code)).difference(
        ["__init__"]
    ), set(
        filter(
            lambda line: re.findall(r"^    \w+\:", line),
            code.splitlines(),
        )
    )


def extract_method_names_and_field_names(
    code: str, file_path: Path, class_extractor: GlobalClassExtractor
) -> tuple[set[str], set[str]]:
    method_names, field_names = set(
        re.findall(r"    def ([^\(]+)\([^\)]+\)[^:]*:", code)
    ).difference(["__init__"]), set(
        filter(
            lambda line: re.findall(r"^    (\w+)\:", line),
            code.splitlines(),
        )
    )
    bases = set(
        map(
            str.strip,
            (re.findall(r"class \w+\(([^\)]+)\)", code) or [""])[0].split(","),
        )
    ).difference(["Protocol"])
    classes = class_extractor.get(file_path).classes
    imports = class_extractor.get(file_path).imports
    _builtin_types = {item[0]: item for item in builtin_types}
    tuple(
        method_names.update(_builtin_types[base][-1])
        for base in bases
        if base in _builtin_types
    )
    _abc_classes = {item[0]: item for item in abc_classes}
    tuple(
        method_names.update(_builtin_types[base][-1])
        for base in bases
        if base in _abc_classes
    )
    tuple(
        tuple(
            (
                method_names.update(
                    (
                        item := extract_method_names_and_field_names(
                            classes[base], file_path, class_extractor
                        )
                    )[0]
                ),
                field_names.update(item[1]),
            )
        )
        for base in bases
        if base in classes
    )
    tuple(
        tuple(
            (
                method_names.update(
                    (
                        item := _extract_from_import(
                            import_path, base, class_extractor
                        )
                    )[0]
                ),
                field_names.update(item[1]),
            )
        )
        for base in bases
        for import_path, imported_names in imports.items()
        if base in imported_names or "*" in imported_names
    )
    return method_names, field_names


def _extract_from_import(
    import_path: str, imported_name: str, class_extractor: GlobalClassExtractor
) -> tuple[set, set]:
    import_file_path = import2path(import_path)
    if not import_file_path.exists():
        return set(), set()
    classes = class_extractor.get(import_file_path).classes
    imports = class_extractor.get(import_file_path).imports
    if imported_name in classes:
        return extract_method_names_and_field_names(
            classes[imported_name], import_file_path, class_extractor
        )
    method_names, field_names = set(), set()
    tuple(
        (
            (
                methods_and_fields := _extract_from_import(
                    import_path, imported_name, class_extractor
                )
            ),
            method_names.update(methods_and_fields[0]),
            field_names.update(methods_and_fields[1]),
        )
        for import_path, imported_names in imports.items()
        if imported_name in imported_names or "*" in imported_names
    )
    return method_names, field_names
