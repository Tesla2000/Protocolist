from __future__ import annotations

import re
import string
from functools import reduce
from operator import itemgetter
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


class TypeAddTransformer(Transformer):
    updated_code: str

    def __init__(self, module: Module, config: Config):
        super().__init__(module, config)
        self.protocols = defaultdict(int)
        self.temp_python_file = self.config.mypy_folder / "_temp.py"

    def leave_FunctionDef(
        self, original_node: "FunctionDef", updated_node: "FunctionDef"
    ) -> "FunctionDef":
        self.updated_code = import_statement + Module([updated_node]).code
        while True:
            protocol_items = tuple(self.protocols.items())
            for key, value in protocol_items:
                for i in range(value):
                    i = str(i + 1)
                    literal = f"Literal['{key + i}']"
                    if literal not in self.updated_code:
                        continue
                    exceptions = self._get_exceptions(
                        self.temp_python_file,
                        self.updated_code.replace(
                            f"Literal['{key + i}']", "None"
                        ),
                    )
                    if not exceptions:
                        self.updated_code = self.updated_code.replace(
                            f"Literal['{key + i}']", "Any"
                        )
                        continue
                    interface = self._get_missing_interface(
                        key + i, exceptions, self.updated_code
                    )
                    self.updated_code = self.updated_code.replace(
                        f"Literal['{key + i}']", interface
                    )
                    self._add_conv_attribute_to_method()
            if len(protocol_items) == len(tuple(self.protocols.items())):
                break
        return updated_node

    def _add_conv_attribute_to_method(self):
        exceptions = self._get_exceptions(
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
        exceptions = self._get_exceptions(
            self.temp_python_file, self.updated_code
        )
        to_many_args_pattern = (
            r"error: Too many arguments for " r"\"([^\"]+)\"\s+\[call-arg\]"
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
                            self.updated_code,
                        )[0],
                    )
                )
                function_signature = self._get_function_signature(
                    function_name, n_args
                )
                self.updated_code = self.updated_code.replace(
                    function_signature,
                    function_signature + f", arg{n_args}",
                )
                exceptions = self._get_exceptions(
                    self.temp_python_file, self.updated_code
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
                        self.updated_code,
                    )[0],
                )
            )
            function_signature = self._get_function_signature(
                function_name, n_args
            )
            self.updated_code = self.updated_code.replace(
                function_signature,
                function_signature + "".join(map(", {}".format, kwarg_names)),
            )

    def _get_missing_interface(
        self, class_name: str, exceptions: Iterable[str], code: str
    ) -> str:
        methods = list(
            method.split("(")[0]
            for pattern, method in _exception2method.items()
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
        valid_iterfaces = tuple(
            (interface, superclasses)
            for interface, superclasses, interface_methods in _abc_classes
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
        protocol = self._create_protocol(class_name, methods)
        rest = self.updated_code.partition(import_statement)[-1]
        self.updated_code = "\n".join(
            (import_statement.strip(), protocol.strip(), rest.strip())
        )
        if not len(valid_iterfaces):
            return self.to_camelcase(class_name)
        return f"Union[{', '.join(
            (
                *tuple(map("collections.abc.".__add__, valid_iterfaces)),
                self.to_camelcase(class_name)
            )
        )}]"

    def _handle_wrong_interface(
        self, exceptions: Iterable[str], updated_code: str
    ) -> str:
        def handle_exception(pattern: str, method: str, code: str) -> str:
            pattern_search = re.compile(pattern).search
            pattern_exceptions = map(
                pattern_search, filter(pattern_search, exceptions)
            )
            for exception in pattern_exceptions:
                type_ = exception.group(1)
                code = code.replace(
                    f"class {type_}(Protocol):",
                    f"class {type_}(Protocol):\n\tdef {method}:\n\t\t...",
                )
            return code

        for pattern, method in _exception2method.items():
            self.updated_code = handle_exception(
                pattern, method, self.updated_code
            )
        return self.updated_code

    def _get_function_signature(self, function_name: str, n_args: int):
        return f"def {function_name}(self" + "".join(
            map(", arg{}".format, map(str, range(n_args)))
        )

    def _create_protocol(self, class_name: str, attr_fields: Iterable[str]):
        attr_fields = set(attr_fields)
        for attr_field in attr_fields:
            self.protocols[attr_field] += 1

        def create_field(attr_field: str) -> str:
            if attr_field in _abc_methods:
                parameters = ", ".join(_abc_method_params[attr_field])
                return f"def {attr_field}({parameters}):\n\t\t..."
            literal_name = attr_field + str(self.protocols[attr_field])
            return f"{attr_field}: Literal['{literal_name}']"

        return (
            f"class {self.to_camelcase(class_name)}(Protocol):\n\t"
            + "\n\t".join(map(create_field, attr_fields))
        )

    @staticmethod
    def to_camelcase(text: str):
        underscores = re.findall(r"_\w", text)
        for underscore in underscores:
            text = text.replace(underscore, underscore[-1])
        return text[0].upper() + text[1:]

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


_exception2method = dict(
    zip(
        (
            r"Value of type \"([^\"]+)\" is not indexable",
            r"has incompatible type \"([^\"]+)\"; expected \"Sized\"",
            r"No overload variant of \"iter\" matches argument type \"([^\"]+)\"",  # noqa: E501
            r"\"([^\"]+)\" has no attribute \"__iter__\"",
            r"No overload variant of \"next\" matches argument type \"([^\"]+)\"",  # noqa: E501
        ),
        (
            "__getitem__(self, index)",
            "__len__(self)",
            "__iter__(self)",
            "__iter__(self)",
            "__next__(self)",
        ),
    )
)
_abc_classes = [
    ("Container", [], ["__contains__"]),
    ("Hashable", [], ["__hash__"]),
    ("Iterable", [], ["__iter__"]),
    ("Iterator", ["Iterable"], ["__next__", "__iter__"]),
    ("Reversible", ["Iterable"], ["__reversed__"]),
    (
        "Generator",
        ["Iterator"],
        ["send", "throw", "close", "__iter__", "__next__"],
    ),
    ("Sized", [], ["__len__"]),
    ("Callable", [], ["__call__"]),
    (
        "Collection",
        ["Sized", "Iterable", "Container"],
        ["__contains__", "__iter__", "__len__"],
    ),
    (
        "Sequence",
        ["Reversible", "Collection"],
        [
            "__getitem__",
            "__len__",
            "__contains__",
            "__iter__",
            "__reversed__",
            "index",
            "count",
        ],
    ),
    (
        "MutableSequence",
        ["Sequence"],
        [
            "__getitem__",
            "__setitem__",
            "__delitem__",
            "__len__",
            "insert",
            "append",
            "clear",
            "reverse",
            "extend",
            "pop",
            "remove",
            "__iadd__",
        ],
    ),
    ("ByteString", ["Sequence"], ["__getitem__", "__len__"]),
    (
        "Set",
        ["Collection"],
        [
            "__contains__",
            "__iter__",
            "__len__",
            "__le__",
            "__lt__",
            "__eq__",
            "__ne__",
            "__gt__",
            "__ge__",
            "__and__",
            "__or__",
            "__sub__",
            "__xor__",
            "isdisjoint",
        ],
    ),
    (
        "MutableSet",
        ["Set"],
        [
            "__contains__",
            "__iter__",
            "__len__",
            "add",
            "discard",
            "clear",
            "pop",
            "remove",
            "__ior__",
            "__iand__",
            "__ixor__",
            "__isub__",
        ],
    ),
    (
        "Mapping",
        ["Collection"],
        [
            "__getitem__",
            "__iter__",
            "__len__",
            "__contains__",
            "keys",
            "items",
            "values",
            "get",
            "__eq__",
            "__ne__",
        ],
    ),
    (
        "MutableMapping",
        ["Mapping"],
        [
            "__getitem__",
            "__setitem__",
            "__delitem__",
            "__iter__",
            "__len__",
            "pop",
            "popitem",
            "clear",
            "update",
            "setdefault",
        ],
    ),
]
_abc_methods = reduce(set.union, map(itemgetter(2), _abc_classes), set())
_abc_method_params = {
    "__and__": ["self", "other"],
    "__call__": ["self", "*args", "**kwargs"],
    "__contains__": ["self", "item"],
    "__delitem__": ["self", "key"],
    "__eq__": ["self", "other"],
    "__ge__": ["self", "other"],
    "__getitem__": ["self", "key"],
    "__gt__": ["self", "other"],
    "__hash__": ["self"],
    "__iadd__": ["self", "other"],
    "__iand__": ["self", "other"],
    "__ior__": ["self", "other"],
    "__isub__": ["self", "other"],
    "__iter__": ["self"],
    "__ixor__": ["self", "other"],
    "__le__": ["self", "other"],
    "__len__": ["self"],
    "__lt__": ["self", "other"],
    "__ne__": ["self", "other"],
    "__next__": ["self"],
    "__or__": ["self", "other"],
    "__reversed__": ["self"],
    "__setitem__": ["self", "key", "value"],
    "__sub__": ["self", "other"],
    "__xor__": ["self", "other"],
    "add": ["self", "element"],
    "append": ["self", "element"],
    "clear": ["self"],
    "close": ["self"],
    "count": ["self", "value"],
    "discard": ["self", "element"],
    "extend": ["self", "iterable"],
    "get": ["self", "key", "default=None"],
    "index": ["self", "value", "start=0", "stop=None"],
    "insert": ["self", "index", "element"],
    "isdisjoint": ["self", "other"],
    "items": ["self"],
    "keys": ["self"],
    "pop": ["self", "key=None"],
    "popitem": ["self"],
    "remove": ["self", "element"],
    "reverse": ["self"],
    "send": ["self", "value"],
    "setdefault": ["self", "key", "default=None"],
    "throw": ["self", "type", "value=None", "traceback=None"],
    "update": ["self", "*args", "**kwargs"],
    "values": ["self"],
}
import_statement = (
    "import collections.abc\nfrom typing import Literal, Protocol, Union\n"
)
