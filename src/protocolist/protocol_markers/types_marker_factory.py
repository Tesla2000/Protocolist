from __future__ import annotations

from ..config import Config
from ..protocol_markers.marker import TypeMarkers
from ..protocol_markers.marker.type_marker import TypeMarker


def create_type_marker(config: Config) -> TypeMarker:
    return next(
        subclass(config)
        for subclass in TypeMarkers
        if subclass.type == config.mark_option
    )
