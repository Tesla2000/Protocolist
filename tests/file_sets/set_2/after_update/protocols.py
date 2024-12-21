from collections.abc import Mapping
from typing import Union, Sequence

SupportsGetItem = Union[Mapping, Sequence, memoryview]
SupportsGetItemAndLength = Union[Mapping, Sequence]