from __future__ import annotations

import re
import string
from itertools import starmap
from pathlib import Path
from typing import Iterable
from typing import Union

import mypy.api
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
from mypy.memprofile import defaultdict

from ..config import Config
from .transformer import Transformer

_exception2method = dict(zip((
                    r"Value of type \"([^\"]+)\" is not indexable",
                    r"has incompatible type \"([^\"]+)\"; expected \"Sized\"",
                    r"No overload variant of \"iter\" matches argument type \"([^\"]+)\"",
                    r"\"([^\"]+)\" has no attribute \"__iter__\"",
                    r"No overload variant of \"next\" matches argument type \"([^\"]+)\"",
                ),
                (
                    "__getitem__(self, index)",
                    "__len__(self)",
                    "__iter__(self)",
                    "__iter__(self)",
                    "__next__(self)",
                )))
class TypeAddTransformer(Transformer):
    def __init__(self, module: Module, config: Config):
        super().__init__(module, config)
        self.protocols = defaultdict(int)

    def leave_FunctionDef(
            self, original_node: "FunctionDef", updated_node: "FunctionDef"
    ) -> "FunctionDef":
        temp_python_file = self.config.mypy_folder / "_temp.py"
        import_statement = (
            "import collections.abc\nfrom typing import Literal, Protocol\n"
        )
        updated_code = import_statement + Module([updated_node]).code
        parameter_pattern = r"Literal\[\'([^\']+)\'\]"
        for _ in range(100):
            exceptions = self._get_exceptions(temp_python_file, updated_code)
            attr_exceptions = list(
                filter(re.compile(r"\[attr\-defined\]$").search, exceptions)
            )
            attr_exceptions = list(
                filter(re.compile(parameter_pattern).search, attr_exceptions)
            )
            if not attr_exceptions:
                break
            attributes = map_reduce(
                attr_exceptions,
                lambda exception: re.findall(parameter_pattern, exception)[0],
                lambda exception: re.findall(
                    r"has no attribute \"([^\"]+)", exception
                )[0],
            )
            protocol_instance = tuple(
                starmap(self._create_protocol, attributes.items())
            )
            protocols = dict(zip(attributes.keys(), protocol_instance))
            _, import_statement, rest = updated_code.partition(
                import_statement
            )
            updated_code = (
                    import_statement + "\n".join(protocols.values()) + "\n" + rest
            )
            for key, value in protocols.items():
                class_name = value.replace("class ", "", 1).split("(")[0]
                updated_code = updated_code.replace(
                    f"Literal['{key}']", class_name
                )
                exceptions = self._get_exceptions(
                    temp_python_file, updated_code
                )
                callable_pattern = r"\"Literal\[\'([^\']+)\'\]\" not callable"
                search = re.compile(callable_pattern).search
                call_exceptions = list(map(search, filter(search, exceptions)))
                for exception in call_exceptions:
                    field_name = exception.group(1)
                    updated_code = updated_code.replace(
                        f"{field_name.rstrip(string.digits)}: "
                        f"Literal['{field_name}']",
                        f"def {field_name.rstrip(string.digits)}"
                        "(self):\n\t\t...",
                    )
                exceptions = self._get_exceptions(
                    temp_python_file, updated_code
                )
                to_many_args_pattern = (
                    r"error: Too many arguments for "
                    r"\"([^\"]+)\"\s+\[call-arg\]"
                )
                search = re.compile(to_many_args_pattern).search
                for _ in range(100):
                    many_args_exceptions = list(
                        map(search, filter(search, exceptions))
                    )
                    for exception in many_args_exceptions:
                        function_name = exception.group(1)
                        n_args = len(
                            re.findall(
                                r"\d+",
                                re.findall(
                                    rf"def {function_name}\(self[\, arg(\d)]+",
                                    updated_code,
                                )[0],
                            )
                        )
                        function_signature = self._get_function_signature(
                            function_name, n_args
                        )
                        updated_code = updated_code.replace(
                            function_signature,
                            function_signature + f", arg{n_args}",
                        )
                        exceptions = self._get_exceptions(
                            temp_python_file, updated_code
                        )
                    if not many_args_exceptions:
                        break
                else:
                    raise ValueError("Issue with number of arguments")
                unexpected_kwargs_pattern = (
                    r"Unexpected keyword argument "
                    r"\"([^\"]+)\" for \"([^\"]+)\"\s+"
                    r"\[call-arg\]"
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
                    n_args = len(
                        re.findall(
                            r"\d+",
                            re.findall(
                                rf"def {function_name}\(self[, arg(\d)]+",
                                updated_code,
                            )[0],
                        )
                    )
                    function_signature = self._get_function_signature(
                        function_name, n_args
                    )
                    updated_code = updated_code.replace(
                        function_signature,
                        function_signature
                        + "".join(map(", {}".format, kwarg_names)),
                    )
        updated_code = self._handle_wrong_interface(exceptions, updated_code)
        for key, value in self.protocols.items():
            for i in range(value):
                i = str(i + 1)
                literal = f"Literal['{key + i}']"
                if literal not in updated_code:
                    continue
                exceptions = self._get_exceptions(
                    temp_python_file,
                    updated_code.replace(f"Literal['{key + i}']", "None"),
                )
                if not exceptions:
                    updated_code = updated_code.replace(f"Literal['{key + i}']", "Any")
                    continue
                interface = self._get_missing_interface(exceptions)
                updated_code = updated_code.replace(f"Literal['{key + i}']", interface)
        return updated_node

    def _get_missing_interface(self, exceptions: Iterable[str]) -> str:
        methods = tuple(method.split("(")[0] for pattern, method in _exception2method.items() if any(map(re.compile(pattern).search, exceptions)))
        if methods == ("__len__", "__iter__"):
            return "collections.abc.Sequence"

    def _handle_wrong_interface(self, exceptions: Iterable[str], updated_code: str) -> str:
        def handle_exception(pattern: str, method: str, code: str) -> str:
            pattern_search = re.compile(pattern).search
            pattern_exceptions = map(pattern_search, filter(pattern_search, exceptions))
            for exception in pattern_exceptions:
                type_ = exception.group(1)
                code = code.replace(f"class {type_}(Protocol):",
                                    f"class {type_}(Protocol):\n\tdef {method}:\n\t\t...")
            return code

        for pattern, method in _exception2method.items():
            updated_code = handle_exception(pattern, method, updated_code)
        return updated_code

    def _get_function_signature(self, function_name: str, n_args: int):
        return f"def {function_name}(self" + "".join(
            map(", arg{}".format, map(str, range(n_args)))
        )

    def _create_protocol(self, param_name: str, attr_fields: Iterable[str]):
        def to_camelcase(text: str):
            underscores = re.findall(r"_\w", text)
            for underscore in underscores:
                text = text.replace(underscore, underscore[-1])
            return text[0].upper() + text[1:]

        attr_fields = set(attr_fields)
        for attr_field in attr_fields:
            self.protocols[attr_field] += 1
        return (
                f"class {to_camelcase(param_name)}(Protocol):\n\t"
                + "\n\t".join(
            f"{attr_field}: Literal['"
            f"{attr_field}{self.protocols[attr_field]}']"
            for attr_field in attr_fields
        )
        )

    def _get_exceptions(self, temp_python_file: Path, updated_code: str):
        temp_python_file.write_text(updated_code)
        return mypy.api.run([str(temp_python_file)])[0].splitlines()[:-1]

    def leave_Param(
            self, original_node: "Param", updated_node: "Param"
    ) -> Union[
        "Param", MaybeSentinel, FlattenSentinel["Param"], RemovalSentinel
    ]:
        if updated_node.annotation is None:
            param_name = updated_node.name.value
            self.protocols[param_name] += 1
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
