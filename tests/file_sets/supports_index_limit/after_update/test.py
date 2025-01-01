from __future__ import annotations

from collections.abc import Mapping
from collections.abc import Sequence
from typing import Union

from tests.file_sets.supports_index_limit.before_update.protocols import Array1


def foo(array: Union[Array1, Mapping, Sequence]) -> None:
    return array[0][0][0]
