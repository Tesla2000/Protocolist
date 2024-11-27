from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from collections.abc import Iterable
from collections.abc import Iterator
from typing import Optional

from tests.src.flashcard_a_i.models.result import Result


class SamplesDivisor(ABC):
    @abstractmethod
    def divide(
        self, results: Iterable[Result]
    ) -> Iterator[Iterator[Optional[Result]]]:
        """
        Divides a collection of results into smaller groups or batches for
        further processing.
        :param results: An iterable collection of Result objects to be divided.
        :return: An iterator of iterators containing optional results.
        """
