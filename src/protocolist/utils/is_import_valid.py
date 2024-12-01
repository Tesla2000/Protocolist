from __future__ import annotations

from collections.abc import Container
from importlib import import_module


def is_import_valid(
    imported_element: str, import_path: str, imported_elements: Container[str]
) -> bool:
    return imported_element in imported_elements or (
        "*" in imported_elements
        and imported_element in dir(import_module(import_path))
    )
