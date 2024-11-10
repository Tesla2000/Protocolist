from __future__ import annotations

from enum import Enum


class PresentationOption(str, Enum):
    PARTIAL_PROTOCOLS = "partial_only"
    COMBINED_PROTOCOLS = "combined_only"
    BOTH = "both"
