from __future__ import annotations

import collections
import typing
from collections.abc import Collection
from collections.abc import Mapping
from collections.abc import Sequence
from functools import partial
from itertools import chain
from itertools import filterfalse
from operator import itemgetter

from protocolist.config import Config
from protocolist.consts import ANY
from protocolist.consts import builtin_types
from protocolist.utils.split_annotations import split_annotations


def extract_annotations(
    annotations: Mapping, protocols: Collection, config: Config
) -> typing.Sequence[str]:
    return tuple(
        annotation
        for annotation in filterfalse(
            tuple(map(itemgetter(0), builtin_types)).__contains__,
            chain.from_iterable(
                map(
                    partial(_remove_any, config=config),
                    map(
                        split_annotations,
                        filter(None, annotations.values()),
                    ),
                )
            ),
        )
        if (
            annotation in protocols
            or annotation in dir(typing)
            or annotation in dir(collections.abc)
            and (annotation != ANY or config.allow_any)
        )
    )


def _remove_any(annotations: Sequence[str], config: Config) -> Sequence[str]:
    if len(annotations) != 1:
        return annotations
    return tuple(
        annotation
        for annotation in annotations
        if annotation != ANY or config.allow_any
    )
