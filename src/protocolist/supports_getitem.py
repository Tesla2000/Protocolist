from __future__ import annotations

from enum import Enum


class SupportsGetitemOption(str, Enum):
    SEQUENCE = "Sequence"
    MAPPING = "Mapping"
    MEMORY_VIEW = "memoryview"
