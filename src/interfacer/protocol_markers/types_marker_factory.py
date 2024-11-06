from src.interfacer.config import Config
from src.interfacer.protocol_markers.marker import TypeMarkers
from src.interfacer.protocol_markers.marker.type_marker import TypeMarker


def create_type_marker(config: Config) -> TypeMarker:
    return next(subclass(config) for subclass in TypeMarkers if subclass.type == config.mark_option)