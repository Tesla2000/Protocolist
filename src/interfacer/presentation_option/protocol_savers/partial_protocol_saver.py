from __future__ import annotations

from ..presentation_option import PresentationOption
from .protocol_saver import ProtocolSaver


class PartialProtocolSaver(ProtocolSaver):
    type = PresentationOption.PARTIAL_PROTOCOLS

    def _modify_protocols(self) -> None:
        pass
