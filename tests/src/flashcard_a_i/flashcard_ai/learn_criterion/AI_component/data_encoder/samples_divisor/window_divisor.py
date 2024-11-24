from __future__ import annotations

from collections.abc import Iterable
from collections.abc import Iterator
from itertools import chain
from typing import Optional

from more_itertools import sliding_window

from tests.src.flashcard_a_i.flashcard_ai.learn_criterion.AI_component.data_encoder.samples_divisor.samples_divisor import (  # noqa: E501
    SamplesDivisor,
)
from tests.src.flashcard_a_i.models.result import Result


class WindowDivisor(SamplesDivisor):
    def __init__(self, n_recent_tries: int):
        """
        Initializes the WindowDivisor class with a specified number of recent
        tries, incremented by one.
        :param n_recent_tries: Specifies the number of recent tries to consider
        for windowing.
        :return: None
        """
        self.n_recent_tries = n_recent_tries + 1

    def divide(
        self, results: Iterable[Result]
    ) -> Iterator[Iterator[Optional[Result]]]:
        """
        Divides a sequence of results into sliding windows of a specified size,
        including padding with None values for recent tries.
        :param results: An iterable collection of Result objects.
        :return: An iterator of sliding windows containing results.
        """
        padding = (self.n_recent_tries - 2) * [None]
        padded_results = chain(padding, results)
        return sliding_window(padded_results, self.n_recent_tries)
