from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from importlib import import_module
from importlib.metadata import packages_distributions
from itertools import chain
from types import ModuleType
from typing import Any
from typing import Iterable
from typing import Optional
from typing import Sequence

from more_itertools import map_except

from src.interfacer.consts import abc_classes
from src.interfacer.consts import builtin_types


@dataclass(slots=True)
class ExternalLibElement:
    item_name: str
    module: ModuleType
    item: Any = None
    module_name: str = None
    fields: Sequence[str] = None
    superclasses: frozenset[str] = None

    def __post_init__(self):
        self.item = getattr(self.module, self.item_name)
        self.module_name = self.module.__name__
        self.fields = dir(self.item)
        self.superclasses = frozenset(
            chain.from_iterable(
                (interface, *superclasses)
                for interface, superclasses, interface_methods in (
                    abc_classes + builtin_types
                )
                if all(map(self.fields.__contains__, interface_methods))
            )
        )
        if self.item.__hash__ is None:
            self.superclasses = frozenset(
                class_ for class_ in self.superclasses if class_ != "Hashable"
            )


@lru_cache
def get_external_library_classes(
    external_libraries: Optional[Iterable[str]],
) -> list[ExternalLibElement]:
    if external_libraries is None:
        external_libraries = packages_distributions().keys()
    modules = tuple(
        map_except(import_module, external_libraries, ModuleNotFoundError)
    )
    return list(
        ExternalLibElement(item_name, module)
        for module in modules
        for item_name in dir(module)
        if not item_name.startswith("_")
        and isinstance(getattr(module, item_name), type)
    )
