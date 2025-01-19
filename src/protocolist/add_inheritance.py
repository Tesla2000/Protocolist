from __future__ import annotations

import re
import string
from itertools import chain
from itertools import product
from pathlib import Path

import libcst

from .config import Config
from .extract_methods_and_fields import extract_method_names_and_field_names
from .get_mypy_exceptions import get_mypy_exceptions
from .protocol_markers.types_marker_factory import create_type_marker
from .transform.class_extractor import ClassExtractor
from .transform.class_extractor import GlobalClassExtractor
from .transform.inheritance_removing_class_extractor import (
    InheritanceRemover,
)


def add_inheritance(
    file_path: Path, config: Config, class_extractor: GlobalClassExtractor
):
    file_content = file_path.read_text()
    interface_content = config.interfaces_path.read_text()
    interface_imports = interface_content.partition("@")[0]
    config.tab_length = config.tab_lengths[file_path]
    file_content = (
        libcst.parse_module(file_content)
        .visit(InheritanceRemover(config, create_type_marker(config)))
        .code.replace(config.tab_length * " ", "\t")
    )
    file_class_extractor = ClassExtractor(config, create_type_marker(config))
    classes = file_class_extractor.extract_classes(file_content)
    file_imports = file_class_extractor.type_marker.imports
    imported_names = set(
        chain.from_iterable(
            value
            for key, value in file_imports.items()
            if key != config.interface_import_path
        )
    )
    all_names = imported_names.union(classes.keys())
    interface_classes = class_extractor.get(config.interfaces_path).classes
    inheritances = []
    class_attributes = {
        key: extract_method_names_and_field_names(
            value, file_path, class_extractor
        )
        for key, value in classes.items()
    }
    interface_attributes = {
        key: extract_method_names_and_field_names(
            value, config.interfaces_path, class_extractor
        )
        for key, value in interface_classes.items()
    }

    def _check_fields_and_methods(item: tuple[str, str]) -> bool:
        class_name, interface_name = item
        if (class_name, interface_name.rstrip(string.digits)) in inheritances:
            return False
        if class_name not in classes:
            return False
        interface_method_names, interface_field_names = interface_attributes[
            interface_name
        ]
        class_method_names, class_field_names = class_attributes[class_name]
        if interface_method_names.difference(class_method_names):
            return False
        return not interface_field_names.difference(class_field_names)

    interface2name = {}
    for class_name, interface_name in filter(
        _check_fields_and_methods,
        product(
            classes.keys(),
            sorted(
                interface_classes.keys(), key=lambda name: name[-1].isnumeric()
            ),
        ),
    ):
        updated_name = interface_name
        while (
            updated_name in all_names and interface_name not in interface2name
        ):
            updated_name += "_"
        all_names.add(updated_name)
        interface2name[interface_name] = interface2name.get(
            interface_name, updated_name
        )
        class_code = classes[class_name]
        class_inheritances = re.findall(
            rf"class {class_name}([^\)^:]*)", class_code
        )[0]
        class_header = f"class {class_name}{class_inheritances}"
        if class_inheritances:
            new_class_code = class_code.replace(
                class_header,
                class_header.rstrip(", ")
                + ", "
                + interface2name[interface_name],
                1,
            )
            updated_file_content = file_content.replace(
                class_code, new_class_code, 1
            )
        else:
            new_class_code = class_code.replace(
                class_header,
                class_header + f"({interface2name[interface_name]})",
                1,
            )
            updated_file_content = file_content.replace(
                class_code, new_class_code, 1
            )
        applicable_interfaces = {
            name: code
            for name, code in interface_classes.items()
            if name == interface_name
            or (
                not interface_name[0].isnumeric()
                and name.rstrip(string.digits) == interface_name
            )
        }
        inheritance_code = re.sub(
            rf"from {config.interface_import_path} import \S+",
            "",
            f"{interface_imports}\n"
            f"{'\n'.join(applicable_interfaces.values())}\n"
            f"{updated_file_content}\n{class_name}()",
        )
        exceptions = get_mypy_exceptions(config.mypy_folder, inheritance_code)
        if any(
            map(
                re.compile(
                    rf"Cannot instantiate abstract class \"{class_name}\" with abstract attribute"  # noqa: E501
                ).search,
                exceptions,
            )
        ):
            continue
        if any(
            any(
                map(
                    re.compile(
                        rf"Incompatible types in assignment \(expression has type \"[^\"]+\", base class \"{name}\""  # noqa: E501
                    ).search,
                    exceptions,
                )
            )
            for name in applicable_interfaces.keys()
        ):
            continue
        if any(
            any(
                map(
                    re.compile(
                        rf"Signature of \"[^\"]+\" incompatible with supertype \"{name}\""  # noqa: E501
                    ).search,
                    exceptions,
                )
            )
            for name in applicable_interfaces.keys()
        ):
            continue
        classes[class_name] = new_class_code
        file_content = updated_file_content
        inheritances.append((class_name, interface_name))
    file_content = (
        "".join(
            set(
                f"from {config.interface_import_path} import {superclass}"
                + bool(interface2name[superclass] != superclass)
                * f" as {interface2name[superclass]}"
                + "\n"
                for _, superclass in inheritances
            )
        )
        + file_content
    ).replace("\t", config.tab_lengths[file_path] * " ")
    result = file_content != file_path.read_text()
    if result:
        print(f"File {file_path} was modified")
        file_path.write_text(file_content)
    return result
