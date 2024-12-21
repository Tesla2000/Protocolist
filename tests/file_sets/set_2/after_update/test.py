from __future__ import annotations

from collections.abc import Mapping
from collections.abc import Sequence
from typing import Union

from tests.file_sets.set_2.before_update.protocols import Array1


def foo(array: Union[Array1, Mapping, Sequence, memoryview]) -> None:
    return array[0][0][0]
