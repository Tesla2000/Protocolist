from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from collections.abc import Iterable

from tests.src.flashcard_a_i.models.result import Result


class ResultsGetter(ABC):
    @abstractmethod
    def get_results(self) -> Iterable[Result]:
        pass
