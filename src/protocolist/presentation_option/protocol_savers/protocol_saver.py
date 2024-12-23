from __future__ import annotations

import importlib.util
import re
import sys
from abc import ABC
from abc import abstractmethod
from collections import OrderedDict
from operator import itemgetter
from pathlib import Path
from typing import Optional

import libcst
from libcst import ClassDef
from libcst import CSTTransformer
from libcst import ImportFrom
from libcst import Module
from more_itertools.more import map_reduce

from ...config import Config
from ...consts import grouped_types
from ...fields_methods_extractor import FieldsAndMethodsExtractor
from ...protocol_markers.types_marker_factory import create_type_marker
from ...transform.class_extractor import ClassExtractor
from ..presentation_option import PresentationOption
from ..replace_partial_with_combined import ReplaceImportsAndNames
from ..replace_partial_with_combined import ReplaceNames


class ProtocolSaver(ABC):
    type: PresentationOption
    replace_dictionary: dict[str, str]

    def __init__(self, config: Config):
        self.config = config

    def modify_protocols(self) -> None:
        self._deduplicate()
        self._modify_protocols()
        self._update_imports_and_names()

    @abstractmethod
    def _modify_protocols(self) -> None:
        pass

    def _deduplicate(self):
        code = self.config.interfaces_path.read_text()
        self.replace_dictionary = {}
        replace_dictionary = None
        while replace_dictionary != self.replace_dictionary:
            replace_dictionary = self.replace_dictionary.copy()
            extracted_classes = ClassExtractor(
                self.config, create_type_marker(self.config)
            ).extract_classes(code)
            grouped_classes = map_reduce(
                extracted_classes.items(),
                lambda item: FieldsAndMethodsExtractor.get_methods_fields_and_bases(  # noqa: E501
                    item[-1]
                ),
            )
            unique_classes = OrderedDict(
                sorted(
                    items,
                    key=lambda item: int(
                        (re.findall(r"\d+", item[0]) or [sys.maxsize])[0]
                    ),
                )[0]
                for items in grouped_classes.values()
            )
            self.replace_dictionary.update(
                {
                    name: next(
                        filter(
                            unique_classes.__contains__,
                            map(itemgetter(0), names),
                        )
                    )
                    for names in grouped_classes.values()
                    for name, _ in names
                }
            )
            self.replace_dictionary = {
                key: self.replace_dictionary[value]
                for key, value in self.replace_dictionary.items()
            }
            imports = code.partition("@")[0]
            code = imports + "".join(unique_classes.values())
            transformer = ReplaceNames(self.config, self.replace_dictionary)
            code = libcst.parse_module(code).visit(transformer).code
        self.config.interfaces_path.write_text(code)

    def _update_imports_and_names(self):
        all_applicable_groups = set()
        for filepath in filter(
            lambda path: path.suffix == ".py", map(Path, self.config.pos_args)
        ):
            module = libcst.parse_module(filepath.read_text())
            names_getter = _LocalNamesGetter(filepath, self.config)
            module.visit(names_getter)
            imports_as = {}
            for key, value in self.replace_dictionary.items():
                while value in names_getter.local_names:
                    value += "_"
                imports_as[key] = value
            visitor = ReplaceImportsAndNames(
                self.config, self.replace_dictionary, imports_as
            )
            code = module.visit(visitor).code
            filepath.write_text(
                "".join(
                    f"from {self.config.interface_import_path}"
                    f" import {group.name}\n"
                    for group in visitor.applicable_groups
                )
                + code
            )
            all_applicable_groups.update(visitor.applicable_groups)
        contents = self.config.interfaces_path.read_text()
        imports, at, rest = contents.partition("@")
        grouped_types_code = "".join(
            f"{group.name} = Union[{', '.join(group.str_types)}]\n"
            for group in all_applicable_groups
        )
        for group in grouped_types:
            imports = imports.replace(f"{group.name} = {group.name}\n", "")
        self.config.interfaces_path.write_text(
            imports + grouped_types_code + at + rest
        )


class _LocalNamesGetter(CSTTransformer):
    def __init__(self, filepath: Path, config: Config):
        super().__init__()
        self.filepath = filepath
        self.config = config
        self.local_names = set()

    def visit_ImportFrom(self, node: "ImportFrom") -> Optional[bool]:
        _, import_path, _, *imported_names = Module([node]).code.split()
        if import_path == self.config.interface_import_path:
            return super().visit_ImportFrom(node)
        self.local_names.update(imported_names)
        if "*" in imported_names:
            spec = importlib.util.spec_from_file_location(
                import_path.rpartition(".")[-1], str(self.filepath)
            )
            self.local_names.update(dir(importlib.util.module_from_spec(spec)))
        return super().visit_ImportFrom(node)

    def visit_ClassDef(self, node: "ClassDef") -> Optional[bool]:
        self.local_names.add(node.name.value)
        return super().visit_ClassDef(node)
