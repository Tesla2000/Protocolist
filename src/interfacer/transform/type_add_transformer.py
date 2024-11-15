from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Optional
from typing import Union

from libcst import FlattenSentinel
from libcst import FunctionDef
from libcst import Lambda
from libcst import MaybeSentinel
from libcst import Module
from libcst import Param
from libcst import RemovalSentinel
from more_itertools import map_reduce

from src.interfacer.config import Config
from src.interfacer.consts import abc_classes
from src.interfacer.consts import ANY
from src.interfacer.consts import builtin_types
from src.interfacer.consts import dunder_method_params
from src.interfacer.consts import dunder_methods
from src.interfacer.consts import exception2method
from src.interfacer.consts import import_statement
from src.interfacer.get_external_library_classes import ExternalLibElement
from src.interfacer.get_external_library_classes import (
    get_external_library_classes,
)  # noqa: E501
from src.interfacer.get_mypy_exceptions import get_mypy_exceptions
from src.interfacer.protocol_markers.marker.type_marker import TypeMarker
from src.interfacer.ProtocolDict import ProtocolDict
from src.interfacer.to_camelcase import to_camelcase
from src.interfacer.transform.class_extractor import ClassExtractor
from src.interfacer.transform.import_visiting_transformer import (
    ImportVisitingTransformer,
)
from src.interfacer.transform.prototype_applier import PrototypeApplier


class TypeAddTransformer(ImportVisitingTransformer):
    updated_code: str
    annotations: dict[str, Optional[str]]

    def __init__(
        self, config: Config, protocol: ProtocolDict, types_marker: TypeMarker
    ):
        super().__init__(types_marker)
        self.config = config
        self.protocols = protocol
        self.temp_python_file = self.config.mypy_folder / "_temp.py"
        self.annotations = {}
        self.imports = set()
        self._lambda_params = set()

    def leave_FunctionDef(
        self, original_node: "FunctionDef", updated_node: "FunctionDef"
    ) -> "FunctionDef":
        self.updated_code = import_statement + Module([updated_node]).code
        while True:
            protocol_items = tuple(self.protocols.items())
            for protocol in self.protocols.get_protocols():
                literal = f"Literal['{protocol}']"
                if literal not in self.updated_code:
                    continue
                exceptions = get_mypy_exceptions(
                    self.temp_python_file,
                    self.updated_code.replace(
                        f"Literal['{protocol}']", "None"
                    ),
                )
                interface = self._get_missing_interface(
                    protocol, exceptions, self.updated_code
                )
                self.updated_code = self.updated_code.replace(
                    f"Literal['{protocol}']", interface
                )
                self._add_conv_attribute_to_method()
                if to_camelcase(protocol) in self.annotations:
                    self.annotations[to_camelcase(protocol)] = interface
            if len(protocol_items) == len(tuple(self.protocols.items())):
                break
        self.save_protocols()
        return self._update_parameters(updated_node)

    def _update_parameters(self, updated_node: FunctionDef) -> FunctionDef:
        module = Module([updated_node])
        new_module = module.visit(
            PrototypeApplier(self.config, self.annotations)
        )
        function_def = new_module.body[0]
        assert isinstance(function_def, FunctionDef)
        return function_def

    def save_protocols(self):
        protocols = self._get_created_protocals()
        for prototype_code in protocols.values():
            self.updated_code = self.updated_code.replace(
                prototype_code.replace(4 * " ", "\t"), "", 1
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
            + "\n".join(
                map(
                    "@runtime_checkable\n{}".format,
                    map(str.lstrip, protocols.values()),
                )
            )
            + "".join(interface_code.partition("@runtime_checkable")[1:])
        )
        self.config.interfaces_path.write_text(interface_code)

    def _get_created_protocals(self) -> dict[str, str]:
        return ClassExtractor(self.type_marker).extract_classes(
            self.updated_code
        )

    def _add_conv_attribute_to_method(self):
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
        exceptions = get_mypy_exceptions(
            self.temp_python_file, self.updated_code
        )
        to_many_args_pattern = (
            r"error: Too many arguments for " r"\"([^\"]+)\""
        )
        search = re.compile(to_many_args_pattern).search
        while True:
            many_args_exceptions = list(
                map(search, filter(search, exceptions))
            )
            if not many_args_exceptions:
                break
            for exception in many_args_exceptions:
                function_name = exception.group(1)
                function_signature = self._get_function_signature(
                    function_name, self.updated_code
                )
                n_args = len(
                    re.findall(
                        r"\d+",
                        function_signature,
                    )
                )
                exceptions = get_mypy_exceptions(
                    self.temp_python_file,
                    self.updated_code.replace(
                        function_signature,
                        function_signature + f", arg{n_args}: None",
                    ),
                )
                hint = self._handle_incompatible_type(
                    function_name, exceptions
                )
                if hint != ANY or self.config.allow_any:
                    self.updated_code = self.updated_code.replace(
                        function_signature,
                        function_signature + f", arg{n_args}: {hint}",
                    )
                else:
                    self.updated_code = self.updated_code.replace(
                        function_signature,
                        function_signature + f", arg{n_args}",
                    )
                exceptions = get_mypy_exceptions(
                    self.temp_python_file, self.updated_code
                )
        unexpected_kwargs_pattern = (
            r"Unexpected keyword argument " r"\"([^\"]+)\" for \"([^\"]+)\""
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
                    function_name, self.updated_code
                )
                exceptions = get_mypy_exceptions(
                    self.temp_python_file,
                    self.updated_code.replace(
                        function_signature,
                        function_signature + f", {kwarg_name}: None",
                    ),
                )
                self.updated_code = self.updated_code.replace(
                    function_signature,
                    function_signature
                    + f", {kwarg_name}: {self._handle_incompatible_type(
                        function_name, exceptions
                    )}",
                )

    def _handle_incompatible_type(
        self, function_name: str, exceptions: list[str]
    ):
        incompatible_type_pattern = rf"Argument \S+ to \"{function_name}\" of \"[^\"]+\" has incompatible type \"([^\"]+)\"; expected \"None\""  # noqa: E501
        incompatible_type_search = re.compile(incompatible_type_pattern).search
        types = tuple(
            {"list[Never]": "list"}.get(type, type)
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

    def _get_missing_interface(
        self, class_name: str, exceptions: Iterable[str], code: str
    ) -> str:
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

        valid_iterfaces = tuple(filter(is_interface_valid, valid_iterfaces))
        valid_external_lib_entries = tuple(
            filter(is_external_lib_valid, external_lib_entries)
        )
        self.imports.update(
            frozenset(
                (entry.item_name, entry.module_name)
                for entry in valid_external_lib_entries
            )
        )
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
        return f"Union[{', '.join(
            (
                *tuple(
                    map(lambda interface: (interface in abc_classes) * "collections.abc." + interface,  # noqa: E501
                        valid_iterfaces
                        )
                ),
                *tuple(
                    map(lambda entry: entry.item_name,
                        valid_external_lib_entries
                        )
                ),
                to_camelcase(class_name)
            )
        )}]"

    def _get_function_signature(
        self, function_name: str, updated_code: str
    ) -> str:
        return re.findall(
            rf"def {function_name}\(self[^)]*",
            updated_code,
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
            f"class {to_camelcase(class_name)}(Protocol):\n\t"
            + "\n\t".join(map(create_field, attr_fields))
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
