from __future__ import annotations

from functools import reduce
from operator import itemgetter

import_statement = (
    "import collections.abc\nfrom collections.abc import *\nfrom typing import Literal, "
    "Protocol, Union, Any, runtime_checkable\n"
)
ANY = "Any"
exception2method = dict(
    zip(
        (
            r"Unsupported target for indexed assignment \(\"([^\"]+)\"\)\s+\[index\]",
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
abc_methods = reduce(set.union, map(itemgetter(2), abc_classes), set())
abc_method_params = {
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