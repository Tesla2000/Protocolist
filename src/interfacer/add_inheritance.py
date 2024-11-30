from __future__ import annotations

import re
from itertools import product
from pathlib import Path

from .config import Config
from .extract_methods_and_fields import extract_method_names_and_field_names
from .get_mypy_exceptions import get_mypy_exceptions
from .protocol_markers.types_marker_factory import create_type_marker
from .transform.class_extractor import GlobalClassExtractor
from .transform.inheritance_removing_class_extractor import (
    InheritanceRemovingClassExtractor,
)


def add_inheritance(
    file_path: Path, config: Config, class_extractor: GlobalClassExtractor
):
    file_content = file_path.read_text()
    interface_content = config.interfaces_path.read_text()
    file_class_extractor = InheritanceRemovingClassExtractor(
        config, create_type_marker(config)
    )
    file_classes = file_class_extractor.extract_classes(file_content)
    interface_classes = class_extractor.get(config.interfaces_path).classes
    inheritances = []
    file_content = file_class_extractor.updated_module.code.replace(
        config.tab_length * " ", "\t"
    )
    class_attributes = {
        key: extract_method_names_and_field_names(
            value, file_path, class_extractor
        )
        for key, value in file_classes.items()
    }
    interface_attributes = {
        key: extract_method_names_and_field_names(
            value, file_path, class_extractor
        )
        for key, value in interface_classes.items()
    }
    classes = class_extractor.get(file_path).classes

    def _check_fields_and_methods(item: tuple[str, str]) -> bool:
        class_name, interface_name = item
        interface_method_names, interface_field_names = interface_attributes[
            interface_name
        ]
        class_method_names, class_field_names = class_attributes[class_name]
        if interface_method_names.difference(class_method_names):
            return False
        return not interface_field_names.difference(class_field_names)

    for class_name, interface_name in filter(
        _check_fields_and_methods,
        product(file_classes.keys(), interface_classes.keys()),
    ):
        class_code = classes[class_name]
        class_inheritances = re.findall(
            rf"class {class_name}([^\)^:]*)", class_code
        )[0]
        class_header = f"class {class_name}{class_inheritances}"
        if class_inheritances:
            new_class_code = class_code.replace(
                class_header,
                class_header.rstrip(", ") + ", " + interface_name,
                1,
            )
            updated_file_content = file_content.replace(
                class_code, new_class_code, 1
            )
        else:
            new_class_code = class_code.replace(
                class_header, class_header + f"({interface_name})", 1
            )
            updated_file_content = file_content.replace(
                class_code, new_class_code, 1
            )
        inheritance_code = re.sub(
            r"from interfaces\.interfaces import \S+",
            "",
            interface_content + updated_file_content + f"\n{class_name}()",
        )
        exceptions = get_mypy_exceptions(
            config.mypy_folder / "_temp.py", inheritance_code
        )
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
            map(
                re.compile(
                    rf"Incompatible types in assignment \(expression has type \"[^\"]+\", base class \"{interface_name}\""  # noqa: E501
                ).search,
                exceptions,
            )
        ):
            continue
        classes[class_name] = new_class_code
        file_content = updated_file_content
        inheritances.append((class_name, interface_name))
    file_content = (
        "".join(
            set(
                f"from {config.interface_import_path} import {superclass}\n"
                for _, superclass in inheritances
            )
        )
        + file_content
    ).replace("\t", config.tab_length * " ")
    result = file_content != file_path.read_text()
    if result:
        print(f"File {file_path} was modified")
    file_path.write_text(file_content)
    return result
