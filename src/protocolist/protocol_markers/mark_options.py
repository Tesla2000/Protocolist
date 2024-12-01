from __future__ import annotations

from enum import Enum


class MarkOption(str, Enum):
    ALL = "all"
    EXTERNAL_LIBRARIES = "external_libraries"
    BUILD_IN = "build_in"
    INTERFACE = "interface"
    EMPTY = "empty"
    NONE = "none"
