from __future__ import annotations

import re
from collections import OrderedDict
from collections.abc import Collection
from collections.abc import Iterable
from collections.abc import Sequence
from functools import partial
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
from ..consts import existing_types
from ..consts import hint_translations
from ..consts import import_statement
from ..consts import open_compatible
from ..consts import protocol_replacement_name
from ..consts import types_parametrized_with_one_parameter
from ..consts import types_parametrized_with_two_parameters
from ..extract_annotations import extract_annotations
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
from ..supports_getitem import SupportsGetitemOption
from ..to_camelcase import to_camelcase
from ..transform.class_extractor import ClassExtractor
from ..transform.class_extractor import GlobalClassExtractor
from ..transform.import_visiting_transformer import (
    ImportVisitingTransformer,
)
from ..transform.prototype_applier import PrototypeApplier
from ..utils.lock import lock


class TypeAddTransformer(ImportVisitingTransformer):
    updated_code: str
    annotations: dict[str, Optional[str]]

    def __init__(
        self,
        config: Config,
        protocol: dict,
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
        self.temp_python_file = self.config.mypy_folder
        self.annotations = {}
        self.imports = set()
        self.full_annotation_to_new = {}
        self._lambda_params = set()
        self._classes_of_methods: dict[FunctionDef, ClassDef] = {}
        self._protocols_with_methods = set()
        self._function_translations = {}

    def leave_FunctionDef(
        self, original_node: "FunctionDef", updated_node: "FunctionDef"
    ) -> "FunctionDef":
        original_code = Module([original_node]).code
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
        self.updated_code = (
            import_statement
            + self._translate_code(
                self.filepath.read_text(), original_code.rstrip(), ""
            ).removesuffix("\n")
            + "\n"
            + updated_function_code
        )
        for _ in range(20):
            protocol_items = tuple(self.protocols.items())
            for protocol in ProtocolDict.get_protocols(self.protocols):
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
        with lock:
            self._save_protocols()
            result = self._update_parameters(updated_node)
            self._function_translations[original_code] = Module([result]).code
            return result

    def _translate_code(self, code: str, original: str, updated: str):
        for key, value in sorted(
            self._function_translations.items(), key=lambda item: -len(item[0])
        ):
            code = code.replace(key, value)
        code = code.replace(original, updated)
        contains_all = type(
            "Protocols",
            tuple(),
            {"__contains__": lambda *args, **kwargs: True},
        )()
        return (
            "".join(
                f"from {self.config.interface_import_path}"
                f" import {annotation}\n"
                for annotation in extract_annotations(
                    self.annotations, contains_all, self.config
                )
            )
            + code
        )

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
                        function_name, exceptions, class_name
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
        self, function_name: str, exceptions: list[str], class_name: str
    ):
        incompatible_type_pattern = rf"Argument \S+ to \"{function_name}\" of \"[^\"]+\" has incompatible type \"([^\"]+)\"; expected \"None\""  # noqa: E501
        incompatible_type_search = re.compile(incompatible_type_pattern).search
        types = tuple(
            hint_translations.get(type, type)
            for type in set(
                map(
                    str.strip,
                    chain.from_iterable(
                        (
                            incompatible_type_exception.group(1).split("|")
                            for incompatible_type_exception in map(
                                incompatible_type_search,
                                filter(incompatible_type_search, exceptions),
                            )
                        )
                    ),
                )
            )
        )
        types = tuple(
            type
            for type in types
            if type != ANY
            and type not in ProtocolDict.get_protocols(self.protocols)
        )
        if not types:
            return ANY
        elif len(types) == 1:
            return types[0]
        return f"Union[{', '.join(types)}]"

    def _get_compatible_interfaces(
        self, patterns: Iterable[str], exceptions: Collection[str]
    ) -> Sequence[set[str]]:
        def get_interfaces(pattern: str):
            pattern_search = re.compile(pattern).search
            return set(
                elem.partition("[")[0]
                for elem in chain.from_iterable(
                    pattern.group(1).split(" | ")
                    for pattern in map(
                        pattern_search, filter(pattern_search, exceptions)
                    )
                )
            ) - {"Literal"}

        return tuple(map(get_interfaces, patterns))

    def _get_missing_interface(self, class_name: str) -> str:
        previous_exceptions = get_mypy_exceptions(
            self.temp_python_file,
            self.new_protocols_code(
                self.updated_code.replace(f"Literal['{class_name}']", ANY)
            ),
        )
        exceptions = set(
            get_mypy_exceptions(
                self.temp_python_file,
                self.new_protocols_code(
                    self.updated_code.replace(
                        f"Literal['{class_name}']", "None"
                    )
                ),
            )
        ).difference(previous_exceptions)
        if not exceptions:
            return ANY
        literal = next(
            chain.from_iterable(
                re.findall(
                    r"Argument 2 to \"[^\"]+\" of \"[^\"]+\" has "
                    r"incompatible type \"None\"; "
                    r"expected \"(Literal\[[^\]]+\])",
                    exception,
                )
                for exception in exceptions
            ),
            None,
        )
        if literal:
            return literal
        method_compatibility_interfaces = self._get_compatible_interfaces(
            [r"has incompatible type \"None\"; expected \"([^\"]+)\""],
            exceptions,
        )[0]
        method_compatibility_interfaces.update(
            open_compatible
            if any(
                self._get_compatible_interfaces(
                    [
                        r"No overload variant of \"open\" matches argument types \"None\", (\"str\")",  # noqa: E501
                        r"No overload variant of \"open\" matches argument types* (\"None\")",  # noqa: E501
                    ],
                    exceptions,
                )
            )
            else tuple()
        )
        method_compatibility_interfaces.update(
            ["int", "float", "complex"]
            if any(
                self._get_compatible_interfaces(
                    [
                        r"No overload variant of \"pow\" matches argument types* (\"None\")",  # noqa: E501
                        r"No overload variant of \"pow\" matches argument types* \"[^\"]+\", (\"None\")",  # noqa: E501
                    ],
                    exceptions,
                )
            )
            else tuple()
        )
        method_compatibility_interfaces.update(
            ["int", "bool"]
            if any(
                self._get_compatible_interfaces(
                    [
                        r"No overload variant of \"range\" matches argument types (\"int\"), (\"int\"), \"None\"",  # noqa: E501
                        r"No overload variant of \"range\" matches argument types (\"int\"), \"None\"",  # noqa: E501
                        r"No overload variant of \"range\" matches argument types* (\"None\")",  # noqa: E501
                    ],
                    exceptions,
                )
            )
            else tuple()
        )
        methods = tuple(
            frozenset(
                method.split("(")[0]
                for pattern, method in exception2method.items()
                if any(map(re.compile(pattern).search, exceptions))
            )
        )
        pattern_search = re.compile(
            r"\"None\" has no attribute \"([^\"]+)\""
        ).search
        attributes = set(
            pattern.group(1)
            for pattern in map(
                pattern_search, filter(pattern_search, exceptions)
            )
        )
        methods = list(attributes.union(methods))
        if not methods:
            method_compatibility_interfaces = set(
                interface
                for interface, superclasses, _ in (abc_classes + builtin_types)
                if not any(
                    map(
                        method_compatibility_interfaces.__contains__,
                        superclasses,
                    )
                )
                and interface in method_compatibility_interfaces
            ).union(
                filterfalse(
                    frozenset(
                        chain.from_iterable(
                            (interface, *superclasses)
                            for interface, superclasses, _ in (
                                abc_classes + builtin_types
                            )
                        )
                    ).__contains__,
                    method_compatibility_interfaces,
                )
            )
            return (
                f"Union[{', '.join(method_compatibility_interfaces)}]"
                if method_compatibility_interfaces
                else ANY
            )
        matching_iterfaces = tuple(
            (interface, superclasses)
            for interface, superclasses, interface_methods in (
                abc_classes + builtin_types
            )
            if all(map(interface_methods.__contains__, methods))
        )
        valid_interface_names = tuple(
            interface for interface, _ in matching_iterfaces
        )
        matching_iterfaces = set(
            interface
            for interface, superclasses in matching_iterfaces
            if not any(map(valid_interface_names.__contains__, superclasses))
        )
        matching_iterfaces = tuple(
            matching_iterfaces.union(
                interface
                for interface in method_compatibility_interfaces
                for interface_name, superclasses, _ in (
                    abc_classes + builtin_types
                )
                if interface == interface_name
                and any(map(superclasses.__contains__, matching_iterfaces))
            )
        )
        external_lib_entries = get_external_library_classes(
            self.config.external_libraries,
            self.config.excluded_libraries,
            methods,
            matching_iterfaces,
        )
        patterns = (
            r'Non-overlapping equality check \(left operand type: "[^"]*None[^"]*", right operand type: "([^"]+)"',  # noqa: E501
            r'Non-overlapping equality check \(left operand type: "([^"]+)", right operand type: "[^"]*None[^"]*"',  # noqa: E501
            r'Invalid index type "([^"]+)" for "[^"]*None[^"]*"',
        )
        matching_iterfaces = tuple(
            set(
                chain.from_iterable(
                    self._get_compatible_interfaces(
                        patterns,
                        exceptions,
                    )
                )
            ).union(matching_iterfaces)
        )

        def is_signature_correct(interface: str, exceptions: set[str]) -> bool:
            new_exceptions = set(exceptions).difference(previous_exceptions)
            return not any(
                re.search(
                    rf"No overload variant of \"[^\"]+\" of \"{interface}\" matches argument",  # noqa: E501
                    exception,
                )
                or re.search(r" has incompatible type ", exception)
                or (
                    re.search(r" Unsupported operand types for ", exception)
                    and not re.search(
                        r"Unsupported operand types for [%\+\*-/]+ "
                        rf"\(\"{interface}\" and \"Literal\['\w+'\]\"",
                        exception,
                    )
                )
                or re.search(r" is not indexable ", exception)
                for exception in new_exceptions
            )

        def is_interface_valid(interface: str) -> bool:
            exceptions = get_mypy_exceptions(
                self.temp_python_file,
                self.updated_code.replace(
                    f"Literal['{class_name}']", interface
                ),
            )
            return is_signature_correct(
                interface,
                exceptions,
            )

        def is_external_lib_valid(element: ExternalLibElement) -> bool:
            exceptions = get_mypy_exceptions(
                self.temp_python_file,
                self.new_protocols_code(
                    f"from {element.module_name} import {element.item_name}\n"
                    + self.updated_code.replace(
                        f"Literal['{class_name}']", element.item_name
                    )
                ),
            )
            exceptions = set(
                f"{str(int(line.split(":", 1)[0]) - 1)}:"
                f"{line.split(":", 1)[-1]}"
                for line in exceptions
            )
            return is_signature_correct(
                element.item_name,
                exceptions,
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
        matching_iterfaces = list(
            self._filter_valid_interfaces(
                matching_iterfaces, method_compatibility_interfaces
            )
        )
        valid_iterfaces = []
        while matching_iterfaces:
            for interface in frozenset(
                interface
                for interface, superclasses, _ in (abc_classes + builtin_types)
                if interface in matching_iterfaces
                and not any(map(matching_iterfaces.__contains__, superclasses))
            ):
                if is_interface_valid(interface):
                    valid_iterfaces.append(interface)
                    for removed_interface in frozenset(
                        interface
                        for interface, superclasses, _ in (
                            abc_classes + builtin_types
                        )
                        if interface in matching_iterfaces
                        and interface in superclasses
                    ):
                        matching_iterfaces.remove(removed_interface)
                matching_iterfaces.remove(interface)
        if not valid_iterfaces and matching_iterfaces:
            return ANY
        valid_iterfaces = tuple(map(add_subtypes, valid_iterfaces))
        valid_elements = [
            *tuple(sorted(map(_add_collections, valid_iterfaces))),
            *tuple(
                sorted(
                    map(
                        lambda entry: entry.item_name,
                        valid_external_lib_entries,
                    )
                )
            ),
        ]
        if (
            not valid_iterfaces and not valid_external_lib_entries
        ) or self.config.add_protocols_on_builtin:
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
                    *valid_elements,
                    to_camelcase(class_name)
                )
            )}]"
        if len(valid_elements) >= 2:
            return f"Union[{', '.join(valid_elements)}]"
        return valid_elements[0]

    def _filter_valid_interfaces(
        self,
        valid_interfaces: Iterable[str],
        method_compatibility_interfaces: Collection[str],
    ) -> Iterable[str]:
        valid_interfaces = tuple(
            filter(
                partial(
                    _is_compatible,
                    compatible_interfaces=method_compatibility_interfaces,
                ),
                valid_interfaces,
            )
        )

        def filter_function(interface: str) -> bool:
            if interface == "memoryview" and self.config.exclude_memoryview:
                return False
            if (
                self.config.supports_getitem_option is None
                or self.config.supports_getitem_option.value
                not in valid_interfaces
            ):
                return True
            return not (
                any(
                    interface == option.value
                    for option in SupportsGetitemOption
                )
                and interface != self.config.supports_getitem_option.value
            )

        return filter(filter_function, valid_interfaces)

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
            camel_case_name = to_camelcase(attr_field)
            with lock:
                self.protocols[camel_case_name] = (
                    self.protocols.get(camel_case_name, 0) + 1
                )

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
            for exception in frozenset(many_args_exceptions):
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
                    function_name, exceptions, class_name
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


def _add_collections(interface: str) -> str:
    return (interface in abc_classes) * "collections.abc." + interface


def _is_compatible(
    interface: str, compatible_interfaces: Collection[str]
) -> bool:
    if not compatible_interfaces:
        return True
    if interface in compatible_interfaces:
        return True
    if interface not in existing_types:
        return True
    return all(
        all(map(superclasses.__contains__, compatible_interfaces))
        for builtin_interface, superclasses, _ in (abc_classes + builtin_types)
        if interface == builtin_interface
    )
