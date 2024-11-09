from __future__ import annotations

from functools import reduce
from operator import itemgetter

import_statement = (
    "import collections.abc\nfrom collections.abc import *\n"
    "from typing import *\nfrom typing import Literal, "
    "Protocol, Union, Any, runtime_checkable\n"
)
ANY = "Any"
exception2method = dict(
    zip(
        (
            r"Unsupported target for indexed assignment \(\"([^\"]+)\"\)\s+\[index\]",  # noqa: E501
            r"Value of type \"([^\"]+)\" is not indexable",
            r"has incompatible type \"([^\"]+)\"; expected \"Sized\"",
            r"No overload variant of \"iter\" matches argument type \"([^\"]+)\"",  # noqa: E501
            r"\"([^\"]+)\" has no attribute \"__iter__\"",
            r'No overload variant of "next" matches argument type "(?!Literal\[)[^"]+"',  # noqa: E501
        ),
        (
            "__setitem__(self, index, value)",
            "__getitem__(self, index)",
            "__len__(self)",
            "__iter__(self)",
            "__iter__(self)",
            "__next__(self)",
        ),
    )
)
abc_classes = [
    ("Container", [], ["__contains__"]),
    ("Hashable", [], ["__hash__"]),
    ("Iterable", [], ["__iter__"]),
    ("Iterator", ["Iterable"], ["__next__", "__iter__"]),
    ("Reversible", ["Iterable"], ["__reversed__"]),
    (
        "Generator",
        ["Iterator", "Iterable"],
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
        [
            "Reversible",
            "Iterable",
            "Collection",
            "Sized",
            "Iterable",
            "Container",
        ],
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
        [
            "Sequence",
            "Reversible",
            "Iterable",
            "Collection",
            "Sized",
            "Iterable",
            "Container",
        ],
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
    (
        "ByteString",
        [
            "Sequence",
            "Reversible",
            "Iterable",
            "Collection",
            "Sized",
            "Iterable",
            "Container",
        ],
        ["__getitem__", "__len__"],
    ),
    (
        "Set",
        ["Collection", "Sized", "Iterable", "Container"],
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
        ["Set", "Collection", "Sized", "Iterable", "Container"],
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
        ["Collection", "Sized", "Iterable", "Container"],
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
        ["Mapping", "Collection", "Sized", "Iterable", "Container"],
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
builtin_types = [
    (
        "int",
        ["Hashable"],
        [
            "__abs__",
            "__add__",
            "__and__",
            "__bool__",
            "__ceil__",
            "__class__",
            "__delattr__",
            "__dir__",
            "__divmod__",
            "__doc__",
            "__eq__",
            "__float__",
            "__floor__",
            "__floordiv__",
            "__format__",
            "__ge__",
            "__getattribute__",
            "__getnewargs__",
            "__getstate__",
            "__gt__",
            "__hash__",
            "__index__",
            "__init__",
            "__init_subclass__",
            "__int__",
            "__invert__",
            "__le__",
            "__lshift__",
            "__lt__",
            "__mod__",
            "__mul__",
            "__ne__",
            "__neg__",
            "__new__",
            "__or__",
            "__pos__",
            "__pow__",
            "__radd__",
            "__rand__",
            "__rdivmod__",
            "__reduce__",
            "__reduce_ex__",
            "__repr__",
            "__rfloordiv__",
            "__rlshift__",
            "__rmod__",
            "__rmul__",
            "__ror__",
            "__round__",
            "__rpow__",
            "__rrshift__",
            "__rshift__",
            "__rsub__",
            "__rtruediv__",
            "__rxor__",
            "__setattr__",
            "__sizeof__",
            "__str__",
            "__sub__",
            "__subclasshook__",
            "__truediv__",
            "__trunc__",
            "__xor__",
            "as_integer_ratio",
            "bit_count",
            "bit_length",
            "conjugate",
            "denominator",
            "from_bytes",
            "imag",
            "is_integer",
            "numerator",
            "real",
            "to_bytes",
        ],
    ),
    (
        "float",
        ["Hashable"],
        [
            "__abs__",
            "__add__",
            "__bool__",
            "__ceil__",
            "__class__",
            "__delattr__",
            "__dir__",
            "__divmod__",
            "__doc__",
            "__eq__",
            "__float__",
            "__floor__",
            "__floordiv__",
            "__format__",
            "__ge__",
            "__getattribute__",
            "__getformat__",
            "__getnewargs__",
            "__getstate__",
            "__gt__",
            "__hash__",
            "__init__",
            "__init_subclass__",
            "__int__",
            "__le__",
            "__lt__",
            "__mod__",
            "__mul__",
            "__ne__",
            "__neg__",
            "__new__",
            "__pos__",
            "__pow__",
            "__radd__",
            "__rdivmod__",
            "__reduce__",
            "__reduce_ex__",
            "__repr__",
            "__rfloordiv__",
            "__rmod__",
            "__rmul__",
            "__round__",
            "__rpow__",
            "__rsub__",
            "__rtruediv__",
            "__setattr__",
            "__sizeof__",
            "__str__",
            "__sub__",
            "__subclasshook__",
            "__truediv__",
            "__trunc__",
            "as_integer_ratio",
            "conjugate",
            "fromhex",
            "hex",
            "imag",
            "is_integer",
            "real",
        ],
    ),
    (
        "complex",
        ["Hashable"],
        [
            "__abs__",
            "__add__",
            "__bool__",
            "__class__",
            "__complex__",
            "__delattr__",
            "__dir__",
            "__doc__",
            "__eq__",
            "__format__",
            "__ge__",
            "__getattribute__",
            "__getnewargs__",
            "__getstate__",
            "__gt__",
            "__hash__",
            "__init__",
            "__init_subclass__",
            "__le__",
            "__lt__",
            "__mul__",
            "__ne__",
            "__neg__",
            "__new__",
            "__pos__",
            "__pow__",
            "__radd__",
            "__reduce__",
            "__reduce_ex__",
            "__repr__",
            "__rmul__",
            "__rpow__",
            "__rsub__",
            "__rtruediv__",
            "__setattr__",
            "__sizeof__",
            "__str__",
            "__sub__",
            "__subclasshook__",
            "__truediv__",
            "conjugate",
            "imag",
            "real",
        ],
    ),
    (
        "bool",
        ["Hashable", "int"],
        [
            "__abs__",
            "__add__",
            "__and__",
            "__bool__",
            "__ceil__",
            "__class__",
            "__delattr__",
            "__dir__",
            "__divmod__",
            "__doc__",
            "__eq__",
            "__float__",
            "__floor__",
            "__floordiv__",
            "__format__",
            "__ge__",
            "__getattribute__",
            "__getnewargs__",
            "__getstate__",
            "__gt__",
            "__hash__",
            "__index__",
            "__init__",
            "__init_subclass__",
            "__int__",
            "__invert__",
            "__le__",
            "__lshift__",
            "__lt__",
            "__mod__",
            "__mul__",
            "__ne__",
            "__neg__",
            "__new__",
            "__or__",
            "__pos__",
            "__pow__",
            "__radd__",
            "__rand__",
            "__rdivmod__",
            "__reduce__",
            "__reduce_ex__",
            "__repr__",
            "__rfloordiv__",
            "__rlshift__",
            "__rmod__",
            "__rmul__",
            "__ror__",
            "__round__",
            "__rpow__",
            "__rrshift__",
            "__rshift__",
            "__rsub__",
            "__rtruediv__",
            "__rxor__",
            "__setattr__",
            "__sizeof__",
            "__str__",
            "__sub__",
            "__subclasshook__",
            "__truediv__",
            "__trunc__",
            "__xor__",
            "as_integer_ratio",
            "bit_count",
            "bit_length",
            "conjugate",
            "denominator",
            "from_bytes",
            "imag",
            "is_integer",
            "numerator",
            "real",
            "to_bytes",
        ],
    ),
    (
        "str",
        [
            "Hashable",
            "Iterable",
            "Reversible",
            "Collection",
            "Container",
            "Sized",
            "Sequence",
        ],
        [
            "__add__",
            "__class__",
            "__contains__",
            "__delattr__",
            "__dir__",
            "__doc__",
            "__eq__",
            "__format__",
            "__ge__",
            "__getattribute__",
            "__getitem__",
            "__getnewargs__",
            "__getstate__",
            "__gt__",
            "__hash__",
            "__init__",
            "__init_subclass__",
            "__iter__",
            "__le__",
            "__len__",
            "__lt__",
            "__mod__",
            "__mul__",
            "__ne__",
            "__new__",
            "__reduce__",
            "__reduce_ex__",
            "__repr__",
            "__rmod__",
            "__rmul__",
            "__setattr__",
            "__sizeof__",
            "__str__",
            "__subclasshook__",
            "capitalize",
            "casefold",
            "center",
            "count",
            "encode",
            "endswith",
            "expandtabs",
            "find",
            "format",
            "format_map",
            "index",
            "isalnum",
            "isalpha",
            "isascii",
            "isdecimal",
            "isdigit",
            "isidentifier",
            "islower",
            "isnumeric",
            "isprintable",
            "isspace",
            "istitle",
            "isupper",
            "join",
            "ljust",
            "lower",
            "lstrip",
            "maketrans",
            "partition",
            "removeprefix",
            "removesuffix",
            "replace",
            "rfind",
            "rindex",
            "rjust",
            "rpartition",
            "rsplit",
            "rstrip",
            "split",
            "splitlines",
            "startswith",
            "strip",
            "swapcase",
            "title",
            "translate",
            "upper",
            "zfill",
        ],
    ),
    (
        "tuple",
        [
            "Hashable",
            "Iterable",
            "Reversible",
            "Collection",
            "Container",
            "Sized",
            "Sequence",
        ],
        [
            "__add__",
            "__class__",
            "__class_getitem__",
            "__contains__",
            "__delattr__",
            "__dir__",
            "__doc__",
            "__eq__",
            "__format__",
            "__ge__",
            "__getattribute__",
            "__getitem__",
            "__getnewargs__",
            "__getstate__",
            "__gt__",
            "__hash__",
            "__init__",
            "__init_subclass__",
            "__iter__",
            "__le__",
            "__len__",
            "__lt__",
            "__mul__",
            "__ne__",
            "__new__",
            "__reduce__",
            "__reduce_ex__",
            "__repr__",
            "__rmul__",
            "__setattr__",
            "__sizeof__",
            "__str__",
            "__subclasshook__",
            "count",
            "index",
        ],
    ),
    (
        "list",
        [
            "MutableSequence",
            "Iterable",
            "Reversible",
            "Collection",
            "Container",
            "Sized",
            "Sequence",
        ],
        [
            "__add__",
            "__class__",
            "__class_getitem__",
            "__contains__",
            "__delattr__",
            "__delitem__",
            "__dir__",
            "__doc__",
            "__eq__",
            "__format__",
            "__ge__",
            "__getattribute__",
            "__getitem__",
            "__getstate__",
            "__gt__",
            "__hash__",
            "__iadd__",
            "__imul__",
            "__init__",
            "__init_subclass__",
            "__iter__",
            "__le__",
            "__len__",
            "__lt__",
            "__mul__",
            "__ne__",
            "__new__",
            "__reduce__",
            "__reduce_ex__",
            "__repr__",
            "__reversed__",
            "__rmul__",
            "__setattr__",
            "__setitem__",
            "__sizeof__",
            "__str__",
            "__subclasshook__",
            "append",
            "clear",
            "copy",
            "count",
            "extend",
            "index",
            "insert",
            "pop",
            "remove",
            "reverse",
            "sort",
        ],
    ),
    (
        "dict",
        [
            "MutableMapping",
            "Iterable",
            "Collection",
            "Container",
            "Sized",
            "Mapping",
        ],
        [
            "__class__",
            "__class_getitem__",
            "__contains__",
            "__delattr__",
            "__delitem__",
            "__dir__",
            "__doc__",
            "__eq__",
            "__format__",
            "__ge__",
            "__getattribute__",
            "__getitem__",
            "__getstate__",
            "__gt__",
            "__hash__",
            "__init__",
            "__init_subclass__",
            "__ior__",
            "__iter__",
            "__le__",
            "__len__",
            "__lt__",
            "__ne__",
            "__new__",
            "__or__",
            "__reduce__",
            "__reduce_ex__",
            "__repr__",
            "__reversed__",
            "__ror__",
            "__setattr__",
            "__setitem__",
            "__sizeof__",
            "__str__",
            "__subclasshook__",
            "clear",
            "copy",
            "fromkeys",
            "get",
            "items",
            "keys",
            "pop",
            "popitem",
            "setdefault",
            "update",
            "values",
        ],
    ),
    (
        "set",
        ["Iterable", "Set", "MutableSet", "Collection", "Container", "Sized"],
        [
            "__and__",
            "__class__",
            "__class_getitem__",
            "__contains__",
            "__delattr__",
            "__dir__",
            "__doc__",
            "__eq__",
            "__format__",
            "__ge__",
            "__getattribute__",
            "__getstate__",
            "__gt__",
            "__hash__",
            "__iand__",
            "__init__",
            "__init_subclass__",
            "__ior__",
            "__isub__",
            "__iter__",
            "__ixor__",
            "__le__",
            "__len__",
            "__lt__",
            "__ne__",
            "__new__",
            "__or__",
            "__rand__",
            "__reduce__",
            "__reduce_ex__",
            "__repr__",
            "__ror__",
            "__rsub__",
            "__rxor__",
            "__setattr__",
            "__sizeof__",
            "__str__",
            "__sub__",
            "__subclasshook__",
            "__xor__",
            "add",
            "clear",
            "copy",
            "difference",
            "difference_update",
            "discard",
            "intersection",
            "intersection_update",
            "isdisjoint",
            "issubset",
            "issuperset",
            "pop",
            "remove",
            "symmetric_difference",
            "symmetric_difference_update",
            "union",
            "update",
        ],
    ),
    (
        "frozenset",
        ["Hashable", "Iterable", "Set", "Collection", "Container", "Sized"],
        [
            "__and__",
            "__class__",
            "__class_getitem__",
            "__contains__",
            "__delattr__",
            "__dir__",
            "__doc__",
            "__eq__",
            "__format__",
            "__ge__",
            "__getattribute__",
            "__getstate__",
            "__gt__",
            "__hash__",
            "__init__",
            "__init_subclass__",
            "__iter__",
            "__le__",
            "__len__",
            "__lt__",
            "__ne__",
            "__new__",
            "__or__",
            "__rand__",
            "__reduce__",
            "__reduce_ex__",
            "__repr__",
            "__ror__",
            "__rsub__",
            "__rxor__",
            "__setattr__",
            "__sizeof__",
            "__str__",
            "__sub__",
            "__subclasshook__",
            "__xor__",
            "copy",
            "difference",
            "intersection",
            "isdisjoint",
            "issubset",
            "issuperset",
            "symmetric_difference",
            "union",
        ],
    ),
    (
        "bytes",
        [
            "Hashable",
            "Iterable",
            "Reversible",
            "ByteString",
            "Collection",
            "Container",
            "Sized",
            "Sequence",
        ],
        [
            "__add__",
            "__buffer__",
            "__bytes__",
            "__class__",
            "__contains__",
            "__delattr__",
            "__dir__",
            "__doc__",
            "__eq__",
            "__format__",
            "__ge__",
            "__getattribute__",
            "__getitem__",
            "__getnewargs__",
            "__getstate__",
            "__gt__",
            "__hash__",
            "__init__",
            "__init_subclass__",
            "__iter__",
            "__le__",
            "__len__",
            "__lt__",
            "__mod__",
            "__mul__",
            "__ne__",
            "__new__",
            "__reduce__",
            "__reduce_ex__",
            "__repr__",
            "__rmod__",
            "__rmul__",
            "__setattr__",
            "__sizeof__",
            "__str__",
            "__subclasshook__",
            "capitalize",
            "center",
            "count",
            "decode",
            "endswith",
            "expandtabs",
            "find",
            "fromhex",
            "hex",
            "index",
            "isalnum",
            "isalpha",
            "isascii",
            "isdigit",
            "islower",
            "isspace",
            "istitle",
            "isupper",
            "join",
            "ljust",
            "lower",
            "lstrip",
            "maketrans",
            "partition",
            "removeprefix",
            "removesuffix",
            "replace",
            "rfind",
            "rindex",
            "rjust",
            "rpartition",
            "rsplit",
            "rstrip",
            "split",
            "splitlines",
            "startswith",
            "strip",
            "swapcase",
            "title",
            "translate",
            "upper",
            "zfill",
        ],
    ),
    (
        "bytearray",
        [
            "MutableSequence",
            "Iterable",
            "Reversible",
            "ByteString",
            "Collection",
            "Container",
            "Sized",
            "Sequence",
        ],
        [
            "__add__",
            "__alloc__",
            "__buffer__",
            "__class__",
            "__contains__",
            "__delattr__",
            "__delitem__",
            "__dir__",
            "__doc__",
            "__eq__",
            "__format__",
            "__ge__",
            "__getattribute__",
            "__getitem__",
            "__getstate__",
            "__gt__",
            "__hash__",
            "__iadd__",
            "__imul__",
            "__init__",
            "__init_subclass__",
            "__iter__",
            "__le__",
            "__len__",
            "__lt__",
            "__mod__",
            "__mul__",
            "__ne__",
            "__new__",
            "__reduce__",
            "__reduce_ex__",
            "__release_buffer__",
            "__repr__",
            "__rmod__",
            "__rmul__",
            "__setattr__",
            "__setitem__",
            "__sizeof__",
            "__str__",
            "__subclasshook__",
            "append",
            "capitalize",
            "center",
            "clear",
            "copy",
            "count",
            "decode",
            "endswith",
            "expandtabs",
            "extend",
            "find",
            "fromhex",
            "hex",
            "index",
            "insert",
            "isalnum",
            "isalpha",
            "isascii",
            "isdigit",
            "islower",
            "isspace",
            "istitle",
            "isupper",
            "join",
            "ljust",
            "lower",
            "lstrip",
            "maketrans",
            "partition",
            "pop",
            "remove",
            "removeprefix",
            "removesuffix",
            "replace",
            "reverse",
            "rfind",
            "rindex",
            "rjust",
            "rpartition",
            "rsplit",
            "rstrip",
            "split",
            "splitlines",
            "startswith",
            "strip",
            "swapcase",
            "title",
            "translate",
            "upper",
            "zfill",
        ],
    ),
    (
        "memoryview",
        ["Iterable", "Sized"],
        [
            "__buffer__",
            "__class__",
            "__delattr__",
            "__delitem__",
            "__dir__",
            "__doc__",
            "__enter__",
            "__eq__",
            "__exit__",
            "__format__",
            "__ge__",
            "__getattribute__",
            "__getitem__",
            "__getstate__",
            "__gt__",
            "__hash__",
            "__init__",
            "__init_subclass__",
            "__iter__",
            "__le__",
            "__len__",
            "__lt__",
            "__ne__",
            "__new__",
            "__reduce__",
            "__reduce_ex__",
            "__release_buffer__",
            "__repr__",
            "__setattr__",
            "__setitem__",
            "__sizeof__",
            "__str__",
            "__subclasshook__",
            "_from_flags",
            "c_contiguous",
            "cast",
            "contiguous",
            "f_contiguous",
            "format",
            "hex",
            "itemsize",
            "nbytes",
            "ndim",
            "obj",
            "readonly",
            "release",
            "shape",
            "strides",
            "suboffsets",
            "tobytes",
            "tolist",
            "toreadonly",
        ],
    ),
    (
        "range",
        [
            "Iterable",
            "Reversible",
            "Collection",
            "Container",
            "Sized",
            "Sequence",
        ],
        [
            "__bool__",
            "__class__",
            "__contains__",
            "__delattr__",
            "__dir__",
            "__doc__",
            "__eq__",
            "__format__",
            "__ge__",
            "__getattribute__",
            "__getitem__",
            "__getstate__",
            "__gt__",
            "__hash__",
            "__init__",
            "__init_subclass__",
            "__iter__",
            "__le__",
            "__len__",
            "__lt__",
            "__ne__",
            "__new__",
            "__reduce__",
            "__reduce_ex__",
            "__repr__",
            "__reversed__",
            "__setattr__",
            "__sizeof__",
            "__str__",
            "__subclasshook__",
            "count",
            "index",
            "start",
            "step",
            "stop",
        ],
    ),
    (
        "slice",
        [],
        [
            "__class__",
            "__delattr__",
            "__dir__",
            "__doc__",
            "__eq__",
            "__format__",
            "__ge__",
            "__getattribute__",
            "__getstate__",
            "__gt__",
            "__hash__",
            "__init__",
            "__init_subclass__",
            "__le__",
            "__lt__",
            "__ne__",
            "__new__",
            "__reduce__",
            "__reduce_ex__",
            "__repr__",
            "__setattr__",
            "__sizeof__",
            "__str__",
            "__subclasshook__",
            "indices",
            "start",
            "step",
            "stop",
        ],
    ),
    (
        "type",
        ["Callable"],
        [
            "__abstractmethods__",
            "__annotations__",
            "__base__",
            "__bases__",
            "__basicsize__",
            "__call__",
            "__class__",
            "__delattr__",
            "__dict__",
            "__dictoffset__",
            "__dir__",
            "__doc__",
            "__eq__",
            "__flags__",
            "__format__",
            "__ge__",
            "__getattribute__",
            "__getstate__",
            "__gt__",
            "__hash__",
            "__init__",
            "__init_subclass__",
            "__instancecheck__",
            "__itemsize__",
            "__le__",
            "__lt__",
            "__module__",
            "__mro__",
            "__name__",
            "__ne__",
            "__new__",
            "__or__",
            "__prepare__",
            "__qualname__",
            "__reduce__",
            "__reduce_ex__",
            "__repr__",
            "__ror__",
            "__setattr__",
            "__sizeof__",
            "__str__",
            "__subclasscheck__",
            "__subclasses__",
            "__subclasshook__",
            "__text_signature__",
            "__type_params__",
            "__weakrefoffset__",
            "mro",
        ],
    ),
]
dunder_methods = tuple(
    filter(
        lambda method: method.startswith("__"),
        reduce(
            set.union, map(itemgetter(2), abc_classes + builtin_types), set()
        ),
    )
)
dunder_method_params = {
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
    "__buffer__": ["self"],
    "__doc__": ["self"],
    "__module__": ["self"],
    "__getstate__": ["self"],
    "__neg__": ["self"],
    "__abs__": ["self"],
    "__setattr__": ["self", "name", "value"],
    "__lshift__": ["self", "other"],
    "__reduce__": ["self"],
    "__pos__": ["self"],
    "__complex__": ["self"],
    "__rdivmod__": ["self", "other"],
    "__subclasses__": ["self"],
    "__dict__": ["self"],
    "__round__": ["self", "n"],
    "__rmod__": ["self", "other"],
    "__subclasshook__": ["cls", "subclass"],
    "__new__": ["cls", "*args", "**kwargs"],
    "__ceil__": ["self"],
    "__truediv__": ["self", "other"],
    "__alloc__": ["self"],
    "__base__": ["self"],
    "__dir__": ["self"],
    "__rxor__": ["self", "other"],
    "__getformat__": ["self", "typestr"],
    "__basicsize__": ["self"],
    "__rrshift__": ["self", "other"],
    "__type_params__": ["self"],
    "__release_buffer__": ["self", "buffer"],
    "__rsub__": ["self", "other"],
    "__trunc__": ["self"],
    "__init_subclass__": ["cls", "**kwargs"],
    "__class_getitem__": ["cls", "key"],
    "__mod__": ["self", "other"],
    "__weakrefoffset__": ["self"],
    "__add__": ["self", "other"],
    "__bytes__": ["self"],
    "__float__": ["self"],
    "__bases__": ["self"],
    "__rmul__": ["self", "other"],
    "__class__": ["self"],
    "__int__": ["self"],
    "__imul__": ["self", "other"],
    "__rfloordiv__": ["self", "other"],
    "__abstractmethods__": ["self"],
    "__bool__": ["self"],
    "__pow__": ["self", "exponent", "modulus=None"],
    "__getnewargs__": ["self"],
    "__subclasscheck__": ["self", "subclass"],
    "__index__": ["self"],
    "__init__": ["self", "*args", "**kwargs"],
    "__divmod__": ["self", "other"],
    "__rand__": ["self", "other"],
    "__getattribute__": ["self", "name"],
    "__delattr__": ["self", "name"],
    "__format__": ["self", "format_spec"],
    "__repr__": ["self"],
    "__invert__": ["self"],
    "__rshift__": ["self", "other"],
    "__prepare__": ["self", "name", "bases", "**kwargs"],
    "__instancecheck__": ["self", "instance"],
    "__itemsize__": ["self"],
    "__reduce_ex__": ["self", "protocol"],
    "__ror__": ["self", "other"],
    "__qualname__": ["self"],
    "__exit__": ["self", "exc_type", "exc_value", "traceback"],
    "__enter__": ["self"],
    "__rtruediv__": ["self", "other"],
    "__flags__": ["self"],
    "__text_signature__": ["self"],
    "__rpow__": ["self", "exponent", "modulus=None"],
    "__mro__": ["self"],
    "__sizeof__": ["self"],
    "__floordiv__": ["self", "other"],
    "__mul__": ["self", "other"],
    "__annotations__": ["self"],
    "__name__": ["self"],
    "__rlshift__": ["self", "other"],
    "__floor__": ["self"],
    "__radd__": ["self", "other"],
    "__str__": ["self"],
    "__dictoffset__": ["self"],
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
