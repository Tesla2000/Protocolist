from __future__ import annotations

from src.interfacer.config import Config
from src.interfacer.presentation_option.protocol_savers import ProtocolSaver
from src.interfacer.presentation_option.protocol_savers import ProtocolSavers


def create_protocol_saver(config: Config) -> ProtocolSaver:
    return next(
        subclass(config)
        for subclass in ProtocolSavers
        if subclass.type == config.protocol_presentation
    )
