from __future__ import annotations

from collections import OrderedDict
from collections.abc import Iterable
from itertools import chain
from itertools import takewhile
from typing import Optional
from uuid import uuid4

from libcst import ClassDef
from libcst import FunctionDef
from libcst import IndentedBlock
from more_itertools.more import always_iterable
from numpy.random.mtrand import Sequence

from src.interfacer.import2path import import2path
from src.interfacer.transform.class_extractor import GlobalClassExtractor


def construct_full_class(
    class_def: ClassDef,
    class_extractor: GlobalClassExtractor,
    previous_classes: OrderedDict[str, "ClassDef"],
    imports: dict[str, Iterable[str]],
) -> ClassDef:
    bases = tuple(base.value.value for base in class_def.bases)

    def _find_base(base_name: str) -> Optional[ClassDef]:
        if base_class := previous_classes.get(base_name):
            return construct_full_class(
                base_class,
                class_extractor,
                OrderedDict(
                    takewhile(
                        lambda item: base_name != item[0],
                        previous_classes.items(),
                    )
                ),
                imports,
            )
        for import_string, imported_names in imports.items():
            if base_name in imported_names or "*" in imported_names:
                extraction_path = import2path(import_string)
                if not extraction_path.exists():
                    return  # base not found
                extracted_values = class_extractor.get(extraction_path)
                class_nodes = extracted_values.class_nodes
                if base_class := class_nodes.get(base_name):
                    return construct_full_class(
                        base_class,
                        class_extractor,
                        OrderedDict(
                            takewhile(
                                lambda item: base_name != item[0],
                                class_nodes.items(),
                            )
                        ),
                        extracted_values.imports,
                    )
        return

    bases = tuple(filter(None, map(_find_base, bases)))
    new_body = _get_new_body(bases, class_def)
    return class_def.with_changes(body=new_body)


def _get_new_body(
    bases: Sequence[ClassDef], class_def: ClassDef
) -> IndentedBlock:
    new_body = OrderedDict()
    for class_ in chain.from_iterable(
        (reversed(bases), always_iterable(class_def))
    ):
        for item in class_.body.body:
            if not isinstance(item, (FunctionDef, ClassDef)):
                new_body[uuid4()] = item
                continue
            new_body[item.name.value] = item
    return class_def.body.with_changes(body=tuple(new_body.values()))
