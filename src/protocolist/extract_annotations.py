from __future__ import annotations

import collections
import typing
from collections.abc import Collection
from collections.abc import Mapping
from itertools import chain
from itertools import filterfalse
from operator import itemgetter

from protocolist.consts import builtin_types
from protocolist.utils.split_annotations import split_annotations


def extract_annotations(
    annotations: Mapping, protocols: Collection
) -> typing.Sequence[str]:
    return tuple(
        annotation
        for annotation in filterfalse(
            tuple(map(itemgetter(0), builtin_types)).__contains__,
            chain.from_iterable(
                map(
                    split_annotations,
                    filter(None, annotations.values()),
                )
            ),
        )
        if (
            annotation in protocols
            or annotation in dir(typing)
            or annotation in dir(collections.abc)
        )
    )
