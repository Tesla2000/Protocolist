from __future__ import annotations

import random
import re
from collections.abc import Iterable
from collections.abc import Sequence
from functools import reduce
from itertools import groupby
from operator import attrgetter
from operator import itemgetter

import libcst
from libcst import FunctionDef
from libcst import Param
from more_itertools.more import map_reduce
from more_itertools.more import unzip

from ...annotation2string import annotation2string
from ...consts import protocol_replacement_name
from ...extract_methods_and_fields import extract_methods_and_fields
from ...protocol_markers.types_marker_factory import create_type_marker
from ...transform.class_extractor import ClassExtractor
from ..presentation_option import PresentationOption
from .protocol_saver import ProtocolSaver


class CombinedProtocolSaver(ProtocolSaver):
    type = PresentationOption.COMBINED_PROTOCOLS

    def _modify_protocols(self) -> None:
        code = self.config.interfaces_path.read_text()
        new_code = code.partition("@")[0]
        class_extractor = ClassExtractor(
            self.config, create_type_marker(self.config)
        )
        classes = class_extractor.extract_classes(code)
        grouped_classes = map_reduce(
            classes.items(),
            lambda item: re.sub(r"\d+", "", item[0]),
            lambda item: item[1],
        )
        for class_name, instances in grouped_classes.items():
            methods, fields = tuple(
                reduce(set.union, stream)
                for stream in unzip(map(extract_methods_and_fields, instances))
            )
            methods = _merge_methods(methods)
            new_code += (
                f"\n@runtime_checkable\nclass {class_name}"
                f"({protocol_replacement_name}):"
                f"\n\t{'\n\t'.join(fields)}\n\t"
                f"{'\n\t'.join(
                    f"{method.rstrip('.')}\n\t\t..." for method in methods)}"
            )
        partial2composite = {
            class_name: re.findall(r"\D+", class_name)[0]
            for class_name in classes.keys()
        }
        self.replace_dictionary = {
            **partial2composite,
            **{
                key: re.findall(r"\D+", value)[0]
                for key, value in self.replace_dictionary.items()
            },
        }
        for partial, composite in partial2composite.items():
            new_code = new_code.replace(partial, composite)
        self.config.interfaces_path.write_text(new_code)


def _merge_methods(methods: Iterable[str]) -> Sequence[str]:
    parsed_methods: Sequence[FunctionDef] = tuple(
        libcst.parse_module(method).body[0] for method in methods
    )
    return tuple(
        _merge_parsed(parsed_methods, method_name)
        for method_name in set(method.name.value for method in parsed_methods)
    )


def _merge_parsed(
    parsed_methods: Sequence[FunctionDef], method_name: str
) -> str:
    most_args_implementations = tuple(
        next(
            groupby(
                sorted(
                    (
                        method.params.params
                        for method in parsed_methods
                        if method.name.value == method_name
                    ),
                    key=len,
                    reverse=True,
                ),
                key=len,
            )
        )[1]
    )
    new_parameters = tuple(
        _merge_parameters(i, most_args_implementations)
        for i in range(len(most_args_implementations[0]))
    )
    params = ", ".join(
        f"{name}{annotation}" for name, annotation in new_parameters
    )
    return f"def {method_name}({params}):"


def _merge_parameters(
    index: int, most_args_implementations: Sequence[Sequence[Param]]
) -> tuple[str, str]:
    parameter_slice = tuple(map(itemgetter(index), most_args_implementations))
    annotations = tuple(map(attrgetter("annotation"), parameter_slice))
    names = tuple(
        implementation.name.value for implementation in parameter_slice
    )
    name = random.choice(
        tuple(name for name in names if name.startswith("arg")) or names
    )
    valid_types = tuple(set(filter(None, map(annotation2string, annotations))))
    return (
        name,
        [
            "",
            f": {valid_types and valid_types[0]}",
            f': Union[{", ".join(valid_types)}]',
        ][min(2, len(valid_types))],
    )
