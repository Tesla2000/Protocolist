from __future__ import annotations

import inspect
from dataclasses import dataclass
from functools import lru_cache
from importlib import import_module
from importlib.metadata import packages_distributions
from itertools import chain
from types import ModuleType
from typing import Any
from typing import Iterable
from typing import Iterator
from typing import Optional
from typing import Sequence

from src.interfacer.consts import abc_classes
from src.interfacer.consts import builtin_types


@dataclass(slots=True)
class ExternalLibElement:
    item_name: str
    module: ModuleType
    item: Any = None
    module_name: str = None
    fields: list[str] = None
    superclasses: frozenset[str] = None

    def __post_init__(self):
        self.item = getattr(self.module, self.item_name)
        if self.item_name in getattr(
            inspect.getmodule(self.item), "__all__", tuple()
        ):
            self.module = inspect.getmodule(self.item)
        self.item = getattr(self.module, self.item_name)
        self.module_name = self.module.__name__
        self.fields = dir(self.item)
        if self.item.__hash__ is None:
            self.fields.remove("__hash__")
        self.superclasses = frozenset(
            chain.from_iterable(
                (interface, *superclasses)
                for interface, superclasses, interface_methods in (
                    abc_classes + builtin_types
                )
                if all(map(self.fields.__contains__, interface_methods))
            )
        )


def _get_modules_recursively(
    module_names: Iterable[str],
    excluded_libraries: Iterable[str],
) -> Iterator[ModuleType]:
    for module_name in module_names:
        try:
            module = import_module(module_name)
        except ModuleNotFoundError:
            continue
        yield module
        yield from _get_modules_recursively(
            (
                f"{module_name}.{attr}"
                for attr in dir(module)
                if isinstance(getattr(module, attr), ModuleType)
                and f"{module_name}.{attr}" not in excluded_libraries
            ),
            excluded_libraries,
        )


@lru_cache
def _get_external_library_classes(
    external_libraries: Optional[Iterable[str]],
    excluded_libraries: Iterable[str],
) -> Iterable[ExternalLibElement]:
    if external_libraries is None:
        external_libraries = packages_distributions().keys()
    modules = set(
        _get_modules_recursively(external_libraries, excluded_libraries)
    )
    return {
        elem.item: elem
        for elem in (
            ExternalLibElement(item_name, module)
            for module in modules
            for item_name in dir(module)
            if not item_name.startswith("_")
            and isinstance(getattr(module, item_name), type)
            and item_name in getattr(module, "__all__", tuple())
        )
    }.values()


def get_external_library_classes(
    external_libraries: Optional[Iterable[str]],
    excluded_libraries: Iterable[str],
    required_methods: Sequence[str],
    valid_iterfaces: Sequence[str],
) -> Sequence[ExternalLibElement]:
    independent_external_lib_elements = tuple(
        filter(
            lambda element: all(
                map(element.fields.__contains__, required_methods)
            )
            and not any(
                map(element.superclasses.__contains__, valid_iterfaces)
            ),
            _get_external_library_classes(
                external_libraries, excluded_libraries
            ),
        )
    )
    independent_items = tuple(
        map(lambda element: element.item, independent_external_lib_elements)
    )
    return tuple(
        filter(
            lambda element: not any(
                map(independent_items.__contains__, element.item.__bases__)
            ),
            independent_external_lib_elements,
        )
    )
