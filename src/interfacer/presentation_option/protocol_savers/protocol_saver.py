from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from ...config import Config
from ..presentation_option import PresentationOption


class ProtocolSaver(ABC):
    type: PresentationOption

    def __init__(self, config: Config):
        self.config = config

    @abstractmethod
    def modify_protocols(self) -> None:
        pass
