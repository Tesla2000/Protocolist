from __future__ import annotations

import re
import string
from typing import Iterable
from typing import Optional
from typing import Union

from libcst import Annotation
from libcst import FlattenSentinel
from libcst import FunctionDef
from libcst import Index
from libcst import LeftSquareBracket
from libcst import MaybeSentinel
from libcst import Module
from libcst import Name
from libcst import Param
from libcst import RemovalSentinel
from libcst import RightSquareBracket
from libcst import SimpleString
from libcst import SimpleWhitespace
from libcst import Subscript
from libcst import SubscriptElement
from more_itertools import map_reduce

from .class_extractor import ClassExtractor
from .prototype_applier import PrototypeApplier
from .transformer import Transformer
from ..ProtocolDict import ProtocolDict
from ..config import Config
from ..consts import import_statement, ANY, abc_method_params, abc_methods, \
    abc_classes, exception2method
from ..get_mypy_exceptions import get_mypy_exceptions
from ..to_camelcase import to_camelcase


class TypeAddTransformer(Transformer):
    updated_code: str
    annotations: dict[str, Optional[str]]

    def __init__(
        self,
        config: Config,
        protocol: ProtocolDict,
    ):
        super().__init__(config)
        self.protocols = protocol
        self.temp_python_file = self.config.mypy_folder / "_temp.py"
        self.annotations = {}

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
                if protocol in self.annotations:
                    self.annotations[protocol] = interface
            if len(protocol_items) == len(tuple(self.protocols.items())):
                break
        self.save_prototypes()
        return self._update_parameters(updated_node)

    def _update_parameters(self, updated_node: FunctionDef) -> FunctionDef:
        module = Module([updated_node])
        new_module = module.visit(
            PrototypeApplier(self.config, self.annotations)
        )
        function_def = new_module.body[0]
        assert isinstance(function_def, FunctionDef)
        return function_def

    def save_prototypes(self):
        prototypes = self._get_created_prototypes()
        for prototype_code in prototypes.values():
            self.updated_code = self.updated_code.replace(
                prototype_code.replace(4 * " ", "\t"), "", 1
            )
        interface_code = ""
        if self.config.interfaces_path.exists():
            interface_code = self.config.interfaces_path.read_text()
        interface_code = (
            import_statement
            + "\n".join(
                map("@runtime_checkable\n{}".format, prototypes.values())
            )
            + interface_code.replace(import_statement, "", 1)
        )
        self.config.interfaces_path.write_text(interface_code)

    def _get_created_prototypes(self) -> dict[str, str]:
        return ClassExtractor.extract_classes(self.updated_code)

    def _add_conv_attribute_to_method(self):
        exceptions = get_mypy_exceptions(
            self.temp_python_file, self.updated_code
        )
        callable_pattern = r"\"Literal\[\'([^\']+)\'\]\" not callable"
        search = re.compile(callable_pattern).search
        call_exceptions = list(map(search, filter(search, exceptions)))
        for exception in call_exceptions:
            field_name = exception.group(1)
            self.updated_code = self.updated_code.replace(
                f"{field_name.rstrip(string.digits)}: "
                f"Literal['{field_name}']",
                f"def {field_name.rstrip(string.digits)}" "(self):\n\t\t...",
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
                        function_signature
                        + f", arg{n_args}: {hint}",
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
            for interface, superclasses, interface_methods in abc_classes
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

        def is_signature_correct(interface: str) -> bool:
            new_exceptions = set(get_mypy_exceptions(self.temp_python_file,
                                                     self.updated_code.replace(
                                                         f"Literal['{class_name}']",
                                                         interface))).difference(
                exceptions)
            return not any(map(re.compile(fr"No overload variant of \"[^\"]+\" of \"{interface}\" matches argument").search, new_exceptions))
        valid_iterfaces = tuple(filter(is_signature_correct, valid_iterfaces))
        protocol = self._create_protocol(class_name, methods)
        rest = self.updated_code.partition(import_statement)[-1]
        self.updated_code = "\n".join(
            (import_statement.strip(), protocol.strip(), rest.strip())
        )
        if not len(valid_iterfaces):
            return to_camelcase(class_name)
        return f"Union[{', '.join(
            (
                *tuple(map("collections.abc.".__add__, valid_iterfaces)),
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
            self.protocols[attr_field] += 1

        def create_field(attr_field: str) -> str:
            if attr_field in filter(
                lambda method: method.startswith("__"), abc_methods
            ):
                parameters = ", ".join(abc_method_params[attr_field])
                return f"def {attr_field}({parameters}):\n\t\t..."
            literal_name = attr_field + str(self.protocols[attr_field])
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
        if updated_node.annotation is None:
            param_name = updated_node.name.value
            if param_name == "self":
                return updated_node
            self.protocols[param_name] += 1
            self.annotations[param_name + str(self.protocols[param_name])] = (
                None
            )
            return updated_node.with_changes(
                annotation=Annotation(
                    annotation=Subscript(
                        value=Name(
                            value="Literal",
                            lpar=[],
                            rpar=[],
                        ),
                        slice=[
                            SubscriptElement(
                                slice=Index(
                                    value=SimpleString(
                                        value=f"'{updated_node.name.value}"
                                        f"{self.protocols[param_name]}'",
                                        lpar=[],
                                        rpar=[],
                                    ),
                                    star=None,
                                    whitespace_after_star=None,
                                ),
                                comma=MaybeSentinel.DEFAULT,
                            ),
                        ],
                        lbracket=LeftSquareBracket(
                            whitespace_after=SimpleWhitespace(
                                value="",
                            ),
                        ),
                        rbracket=RightSquareBracket(
                            whitespace_before=SimpleWhitespace(
                                value="",
                            ),
                        ),
                        lpar=[],
                        rpar=[],
                        whitespace_after_value=SimpleWhitespace(
                            value="",
                        ),
                    ),
                    whitespace_before_indicator=SimpleWhitespace(
                        value="",
                    ),
                    whitespace_after_indicator=SimpleWhitespace(
                        value=" ",
                    ),
                )
            )
        return updated_node
