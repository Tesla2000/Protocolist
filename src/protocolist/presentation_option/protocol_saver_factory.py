from __future__ import annotations

from ..config import Config
from ..presentation_option.protocol_savers import ProtocolSaver
from ..presentation_option.protocol_savers import ProtocolSavers


def create_protocol_saver(config: Config) -> ProtocolSaver:
    return next(
        subclass(config)
        for subclass in ProtocolSavers
        if subclass.type == config.protocol_presentation
    )
