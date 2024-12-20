from __future__ import annotations

import re
from collections import OrderedDict
from collections.abc import Iterable
from itertools import chain
from itertools import filterfalse
from pathlib import Path
from typing import Optional
from typing import Union

import libcst
from libcst import ClassDef
from libcst import FlattenSentinel
from libcst import FunctionDef
from libcst import Lambda
from libcst import MaybeSentinel
from libcst import Module
from libcst import Param
from libcst import RemovalSentinel
from more_itertools import map_reduce

from ..config import Config
from ..construct_full_class import construct_full_class
from ..consts import abc_classes
from ..consts import ANY
from ..consts import builtin_types
from ..consts import dunder_method_params
from ..consts import dunder_methods
from ..consts import exception2method
from ..consts import hint_translations
from ..consts import import_statement
from ..consts import protocol_replacement_name
from ..consts import types_parametrized_with_one_parameter
from ..consts import types_parametrized_with_two_parameters
from ..get_external_library_classes import ExternalLibElement
from ..get_external_library_classes import (
    get_external_library_classes,
)
from ..get_mypy_exceptions import get_mypy_exceptions
from ..protocol_dict import ProtocolDict
from ..protocol_markers.marker.type_marker import TypeMarker
from ..protocol_markers.types_marker_factory import (
    create_type_marker,
)
from ..to_camelcase import to_camelcase
from ..transform.class_extractor import ClassExtractor
from ..transform.class_extractor import GlobalClassExtractor
from ..transform.import_visiting_transformer import (
    ImportVisitingTransformer,
)
from ..transform.prototype_applier import PrototypeApplier


class TypeAddTransformer(ImportVisitingTransformer):
    updated_code: str
    annotations: dict[str, Optional[str]]

    def __init__(
        self,
        config: Config,
        protocol: ProtocolDict,
        types_marker: TypeMarker,
        class_extractor: GlobalClassExtractor,
        filepath: Path,
    ):
        super().__init__(config, types_marker)
        self._previous_classes = OrderedDict()
        self.class_extractor = class_extractor
        self.config = config
        self.protocols = protocol
        self.filepath = filepath
        self.temp_python_file = self.config.mypy_folder / "_temp.py"
        self.annotations = {}
        self.imports = set()
        self.full_annotation_to_new = {}
        self._lambda_params = set()
        self._classes_of_methods: dict[FunctionDef, ClassDef] = {}
        self._protocols_with_methods = set()

    def leave_FunctionDef(
        self, original_node: "FunctionDef", updated_node: "FunctionDef"
    ) -> "FunctionDef":
        if original_node in self._classes_of_methods:
            class_ = self._classes_of_methods[original_node]
            updated_function_code = Module(
                [
                    class_.with_changes(
                        body=class_.body.with_changes(
                            body=tuple(
                                updated_node if elem == original_node else elem
                                for elem in class_.body.body
                            )
                        )
                    )
                ]
            ).code
        else:
            updated_function_code = Module([updated_node]).code
        self.updated_code = import_statement + updated_function_code
        for _ in range(20):
            protocol_items = tuple(self.protocols.items())
            for protocol in self.protocols.get_protocols():
                literal = f"Literal['{protocol}']"
                if literal not in self.updated_code:
                    continue
                interface_ = self._get_missing_interface(protocol)
                interface = self._combine_saved_and_new_interface(
                    interface_, protocol
                )
                self.full_annotation_to_new[interface] = interface_
                self.updated_code = self.updated_code.replace(
                    f"Literal['{protocol}']", interface
                )
                self._conv_attribute_to_method()
                if to_camelcase(protocol) in self.annotations:
                    self.annotations[to_camelcase(protocol)] = interface
            if protocol_items == tuple(self.protocols.items()):
                break
        else:
            raise ValueError
        self._save_protocols()
        return self._update_parameters(updated_node)

    def new_protocols_code(self, code: str) -> str:
        for full_annotation, new_annotation in sorted(
            self.full_annotation_to_new.items(), key=lambda item: -len(item[0])
        ):
            code = code.replace(f": {full_annotation}", f": {new_annotation}")
        return code

    def visit_ClassDef(self, node: "ClassDef") -> Optional[bool]:
        full_class_node = construct_full_class(
            node,
            self.class_extractor,
            self._previous_classes,
            self.type_marker.imports,
        )
        self._previous_classes[node.name.value] = node
        for method in filter(
            FunctionDef.__instancecheck__, full_class_node.body.body
        ):
            self._classes_of_methods[method] = full_class_node
        return super().visit_ClassDef(full_class_node)

    def _update_parameters(self, updated_node: FunctionDef) -> FunctionDef:
        module = Module([updated_node])
        new_module = module.visit(
            PrototypeApplier(self.config, self.annotations)
        )
        function_def = new_module.body[0]
        assert isinstance(function_def, FunctionDef)
        return function_def

    def _save_protocols(self):
        protocols = self._get_created_protocols()
        for prototype_code in protocols.values():
            self.updated_code = self.updated_code.replace(
                prototype_code.replace(self.config.tab_length * " ", "\t"),
                "",
                1,
            )
        interface_code = import_statement
        if self.config.interfaces_path.exists():
            interface_code = (
                self.config.interfaces_path.read_text() or interface_code
            )
        interface_code = (
            interface_code.partition("@runtime_checkable")[0]
            + "".join(
                set(
                    f"from {module_name} import {item_name}\n"
                    for item_name, module_name in dict(self.imports).items()
                )
            )
            + "".join(interface_code.partition("@runtime_checkable")[1:])
            + "\n".join(
                map(
                    "@runtime_checkable\n{}".format,
                    map(str.lstrip, protocols.values()),
                )
            )
        )
        self.config.interfaces_path.write_text(interface_code)

    def _get_created_protocols(self) -> dict[str, str]:
        return ClassExtractor(self.config, self.type_marker).extract_protocols(
            self.updated_code
        )

    def _conv_attribute_to_method(self):
        exceptions = get_mypy_exceptions(
            self.temp_python_file, self.updated_code
        )
        callable_pattern = r"\"Literal\[\'([^\']+)\'\]\" not callable"
        search = re.compile(callable_pattern).search
        call_exceptions = list(map(search, filter(search, exceptions)))
        for exception in call_exceptions:
            literal_name = exception.group(1)
            field_name = re.findall(
                rf"(\S+): Literal\[\'{literal_name}\'\]", self.updated_code
            )
            if field_name:
                self.updated_code = self.updated_code.replace(
                    f"{field_name[0]}: " f"Literal['{literal_name}']",
                    f"def {field_name[0]}" "(self):\n\t\t...",
                )
        classes = ClassExtractor(
            self.config, create_type_marker(self.config)
        ).extract_classes(self.updated_code)
        for class_name, class_code in classes.items():
            if class_name in self._protocols_with_methods:
                continue
            class_code = class_code.strip().replace(
                self.config.tab_length * " ", "\t"
            )
            commented_classes = 0
            for _class_code in map(
                classes.get,
                filterfalse(
                    class_name.__eq__,
                    filterfalse(
                        self._protocols_with_methods.__contains__, classes
                    ),
                ),
            ):
                _class_code = _class_code.strip().replace(
                    self.config.tab_length * " ", "\t"
                )
                self.updated_code = self.updated_code.replace(
                    _class_code, f"'''\n{_class_code}\n'''", 1
                )
                commented_classes += 1
            class_code = self._add_args(class_code, class_name)
            exceptions = get_mypy_exceptions(
                self.temp_python_file, self.updated_code
            )
            unexpected_kwargs_pattern = (
                r"Unexpected keyword argument "
                r"\"([^\"]+)\" for \"([^\"]+)\""
            )
            search = re.compile(unexpected_kwargs_pattern).search
            unexpected_kwargs_exceptions = map_reduce(
                map(search, filter(search, exceptions)),
                lambda exception: exception.group(2),
                lambda exception: exception.group(1),
            )
            for (
                function_name,
                kwarg_names,
            ) in unexpected_kwargs_exceptions.items():
                for kwarg_name in set(kwarg_names):
                    function_signature = self._get_function_signature(
                        function_name, class_code
                    )
                    if function_signature is None:
                        continue
                    exceptions = get_mypy_exceptions(
                        self.temp_python_file,
                        self.updated_code.replace(
                            class_code,
                            class_code.replace(
                                function_signature,
                                function_signature + f", {kwarg_name}: None",
                                1,
                            ),
                        ),
                    )
                    compatible_type = self._handle_incompatible_type(
                        function_name, exceptions
                    )
                    self.updated_code = self.updated_code.replace(
                        class_code,
                        class_code.replace(
                            function_signature,
                            function_signature
                            + f", {kwarg_name}: {compatible_type}",
                            1,
                        ),
                    )
            self.updated_code = self.updated_code.replace(
                "'''", "", 2 * commented_classes
            )
            self._protocols_with_methods.add(class_name)

    def _handle_incompatible_type(
        self, function_name: str, exceptions: list[str]
    ):
        incompatible_type_pattern = rf"Argument \S+ to \"{function_name}\" of \"[^\"]+\" has incompatible type \"([^\"]+)\"; expected \"None\""  # noqa: E501
        incompatible_type_search = re.compile(incompatible_type_pattern).search
        types = tuple(
            hint_translations.get(type, type)
            for type in set(
                incompatible_type_exception.group(1)
                for incompatible_type_exception in map(
                    incompatible_type_search,
                    filter(incompatible_type_search, exceptions),
                )
            )
        )
        if not types:
            return ANY
        elif len(types) == 1:
            return types[0]
        return f"Union[{', '.join(types)}]"

    def _get_missing_interface(self, class_name: str) -> str:
        exceptions = get_mypy_exceptions(
            self.temp_python_file,
            self.new_protocols_code(
                self.updated_code.replace(f"Literal['{class_name}']", "None")
            ),
        )
        exceptions = frozenset(exceptions)
        if not exceptions:
            return ANY
        methods = list(
            method.split("(")[0]
            for pattern, method in exception2method.items()
            if any(map(re.compile(pattern).search, exceptions))
        )
        pattern_search = re.compile(
            r"\"None\" has no attribute \"([^\"]+)\""
        ).search
        attributes = list(
            set(
                pattern.group(1)
                for pattern in map(
                    pattern_search, filter(pattern_search, exceptions)
                )
            )
        )
        methods += attributes
        if not methods:
            return ANY
        valid_iterfaces = tuple(
            (interface, superclasses)
            for interface, superclasses, interface_methods in (
                abc_classes + builtin_types
            )
            if all(map(interface_methods.__contains__, methods))
        )
        valid_interface_names = tuple(
            interface for interface, _ in valid_iterfaces
        )
        valid_iterfaces = tuple(
            interface
            for interface, superclasses in valid_iterfaces
            if not any(map(valid_interface_names.__contains__, superclasses))
        )
        external_lib_entries = get_external_library_classes(
            self.config.external_libraries,
            self.config.excluded_libraries,
            methods,
            valid_iterfaces,
        )

        def is_signature_correct(interface: str, updated_code: str) -> bool:
            new_exceptions = set(
                get_mypy_exceptions(
                    self.temp_python_file,
                    updated_code,
                )
            ).difference(exceptions)
            return not any(
                re.search(
                    rf"No overload variant of \"[^\"]+\" of \"{interface}\" matches argument",  # noqa: E501
                    exception,
                )
                or re.search(" has incompatible type ", exception)
                or re.search(r" Unsupported operand types for ", exception)
                for exception in new_exceptions
            )

        def is_interface_valid(interface: str) -> bool:
            return is_signature_correct(
                interface,
                self.updated_code.replace(
                    f"Literal['{class_name}']", interface
                ),
            )

        def is_external_lib_valid(element: ExternalLibElement) -> bool:
            return is_signature_correct(
                element.item_name,
                f"from {element.module_name} import {element.item_name}\n"
                + self.updated_code.replace(
                    f"Literal['{class_name}']", element.item_name
                ),
            )

        def add_subtypes(interface: str) -> str:
            if interface in types_parametrized_with_one_parameter:
                subscript = class_name + "Subscript"
                new = f"{interface}[Literal['{subscript}']]"
                self.updated_code = self.updated_code.replace(
                    f"Literal['{class_name}']",
                    new,
                    1,
                )
                subscription = self._get_missing_interface(subscript)
                self.updated_code = self.updated_code.replace(
                    new,
                    f"Literal['{class_name}']",
                    1,
                )
                new_interface = interface + f"[{subscription}]"
                if (subscription != ANY or self.config.allow_any) and len(
                    new_interface
                ) <= self.config.max_hint_length:
                    return new_interface
                return interface
            if interface in types_parametrized_with_two_parameters:
                subscript = class_name + "FirstSubscript"
                new = (
                    f"{interface}[Literal["
                    f"'{class_name + "FirstSubscript"}'], Any]"
                )
                self.updated_code = self.updated_code.replace(
                    f"Literal['{class_name}']",
                    new,
                    1,
                )
                subscription1 = self._get_missing_interface(subscript)
                subscript = class_name + "SecondSubscript"
                self.updated_code = self.updated_code.replace(
                    new,
                    f"{interface}[{subscription1}, Literal['{subscript}']]",
                    1,
                )
                subscription2 = self._get_missing_interface(subscript)
                self.updated_code = self.updated_code.replace(
                    f"{interface}[{subscription1}, Literal['{subscript}']]",
                    f"Literal['{class_name}']",
                    1,
                )
                new_interface = (
                    interface + f"[{subscription1}, {subscription2}]"
                )
                if (
                    subscription1 != ANY
                    or subscription2 != ANY
                    or self.config.allow_any
                ) and len(new_interface) <= self.config.max_hint_length:
                    return new_interface
                return interface
            return interface

        valid_external_lib_entries = tuple(
            filter(is_external_lib_valid, external_lib_entries)
        )
        self.imports.update(
            frozenset(
                (entry.item_name, entry.module_name)
                for entry in valid_external_lib_entries
            )
        )
        valid_iterfaces = tuple(filter(is_interface_valid, valid_iterfaces))
        valid_iterfaces = tuple(map(add_subtypes, valid_iterfaces))
        protocol = self._create_protocol(class_name, methods)
        rest = self.updated_code.partition(import_statement)[-1]
        self.updated_code = "\n".join(
            (
                import_statement.strip(),
                "\n".join(
                    f"from {entry.module_name} import {entry.item_name}"
                    for entry in valid_external_lib_entries
                ),
                protocol.strip(),
                rest.strip(),
            )
        )
        if not valid_iterfaces and not valid_external_lib_entries:
            return to_camelcase(class_name)

        def add_collections(interface: str) -> str:
            return (interface in abc_classes) * "collections.abc." + interface

        return f"Union[{', '.join(
            (
                *tuple(
                    sorted(map(add_collections,
                               valid_iterfaces
                               ))
                ),
                *tuple(
                    sorted(map(lambda entry: entry.item_name,
                               valid_external_lib_entries
                               ))
                ),
                to_camelcase(class_name)
            )
        )}]"

    def _get_function_signature(
        self, function_name: str, updated_code: str
    ) -> Optional[str]:
        return (
            re.findall(
                rf"def {function_name}\(self[^)]*",
                updated_code,
            )
            or [None]
        )[0]

    def _create_protocol(self, class_name: str, attr_fields: Iterable[str]):
        attr_fields = set(attr_fields)
        for attr_field in attr_fields:
            self.protocols[to_camelcase(attr_field)] += 1

        def create_field(attr_field: str) -> str:
            if attr_field in dunder_methods:
                parameters = ", ".join(dunder_method_params[attr_field])
                return f"def {attr_field}({parameters}):\n\t\t..."
            literal_name = to_camelcase(attr_field) + str(
                self.protocols[to_camelcase(attr_field)]
            )
            return f"{attr_field}: Literal['{literal_name}']"

        return (
            f"class {to_camelcase(class_name)}"
            f"({protocol_replacement_name}):\n\t"
            + "\n\t".join(map(create_field, sorted(attr_fields)))
        )

    def leave_Param(
        self, original_node: "Param", updated_node: "Param"
    ) -> Union[
        "Param", MaybeSentinel, FlattenSentinel["Param"], RemovalSentinel
    ]:
        if original_node in self._lambda_params:
            return updated_node
        return self.type_marker.conv_parameter(
            updated_node, self.protocols, self.annotations
        )

    def visit_Lambda_params(self, node: "Lambda") -> None:
        self._lambda_params.update(set(node.params.params))
        return super().visit_Lambda_params(node)

    def _combine_saved_and_new_interface(
        self, new_interface: str, protocol: str
    ) -> str:
        old_interface = self.type_marker.saved_annotations.get(protocol)
        if old_interface is None:
            return new_interface
        if new_interface == ANY and not self.config.allow_any:
            return old_interface
        new_elements = divided_to_sub_elements(new_interface)
        old_elements = divided_to_sub_elements(old_interface)
        combined_elements = tuple(
            chain.from_iterable(
                (
                    old_elements,
                    sorted(set(new_elements).difference(old_elements)),
                )
            )
        )
        if len(combined_elements) == 1:
            return tuple(combined_elements)[0]
        return f"Union[{', '.join(combined_elements)}]"

    def _add_args(self, class_code: str, class_name: str) -> str:
        exceptions = get_mypy_exceptions(
            self.temp_python_file, self.updated_code
        )
        to_many_args_pattern = (
            r"error: Too many arguments for " r"\"([^\"]+)\""
        )
        search = re.compile(to_many_args_pattern).search

        def get_signature(match: re.Match) -> Optional[str]:
            return self._get_function_signature(match.group(1), class_code)

        new_class_code = class_code
        for _ in range(100):

            many_args_exceptions = list(
                map(search, filter(search, exceptions))
            )
            if not any(filter(None, map(get_signature, many_args_exceptions))):
                return new_class_code
            for exception in many_args_exceptions:
                function_name = exception.group(1)
                function_signature = self._get_function_signature(
                    function_name, class_code
                )
                if function_signature is None:
                    continue
                n_args = len(
                    re.findall(
                        r"\d+",
                        function_signature,
                    )
                )
                exceptions = get_mypy_exceptions(
                    self.temp_python_file,
                    self.updated_code.replace(
                        class_code,
                        class_code.replace(
                            function_signature,
                            function_signature + f", arg{n_args}: None",
                            1,
                        ),
                    ),
                )
                to_little_args_pattern = (
                    r"error: Missing positional argument "
                    f'"arg{n_args}" in call to '
                    f'"{function_name}" of "{class_name}"'
                )
                if any(
                    map(re.compile(to_little_args_pattern).search, exceptions)
                ):
                    return new_class_code
                hint = self._handle_incompatible_type(
                    function_name, exceptions
                )
                if hint != ANY or self.config.allow_any:
                    new_class_code = class_code.replace(
                        function_signature,
                        function_signature + f", arg{n_args}: {hint}",
                        1,
                    )
                else:
                    new_class_code = class_code.replace(
                        function_signature,
                        function_signature + f", arg{n_args}",
                        1,
                    )
                self.updated_code = self.updated_code.replace(
                    class_code, new_class_code
                )
                class_code = new_class_code
                exceptions = get_mypy_exceptions(
                    self.temp_python_file, self.updated_code
                )
        raise ValueError


def divided_to_sub_elements(interface: str) -> set[str]:
    new_elements = set(
        Module([slice]).code.strip(", ")
        for slice in getattr(libcst.parse_expression(interface), "slice", [])
    )
    if (
        not len(new_elements)
        or (
            len(new_elements) < 2
            and interface.partition("[")[0]
            in types_parametrized_with_one_parameter
        )
        or (
            len(new_elements) < 3
            and interface.partition("[")[0]
            in types_parametrized_with_two_parameters
        )
    ):
        return {interface}
    return new_elements
