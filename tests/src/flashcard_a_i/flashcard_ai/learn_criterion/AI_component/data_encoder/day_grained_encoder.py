from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from itertools import chain
from typing import Optional

from numpy import array
from numpy import ndarray

from tests.src.flashcard_a_i.flashcard_ai.learn_criterion.AI_component.data_encoder.data_encoder import (  # noqa: E501
    DataEncoder,
)
from tests.src.flashcard_a_i.models.result import Result


class DayGrainedDataEncoder(DataEncoder):
    def encode_x_sample(
        self, sample: Iterable[Optional[Result]]
    ) -> tuple[ndarray, int]:
        """
        The `encode_x_sample` function takes an iterable of optional `Result`
        objects and encodes each result into a tuple containing an integer
        indicating correctness and the number of days since the result's date,
        returning a flattened NumPy array of these encoded values. If a result
        is `None`, it assigns a default value of -1 for correctness and 1000
        for the days.
        :param sample: An iterable collection of optional Result objects, where
        each Result may contain information about correctness and a date.
        :return: A tuple containing an ndarray of encoded results and an
        integer representing the sample size.
        """

        def encode_result(result: Optional[Result]) -> tuple[int, int]:
            """
            The `encode_result` function takes an optional `Result` object and
            returns a tuple containing an integer indicating whether the result is
            correct (1 for correct, 0 for incorrect) and the number of days since
            the result's date, or returns (-1, 1000) if the input is `None`.
            :param result: An optional Result object that indicates whether a task
            was completed correctly and the duration since its completion in days.
            :return: A tuple containing a correctness indicator and the number of
            days since the result date, or (-1, 1000) if the result is None.
            """  # noqa: E501
            if result is None:
                return -1, 1000
            return int(result.is_correct), (datetime.now() - result.date).days

        encoded = map(encode_result, sample)
        return array(tuple(chain.from_iterable(encoded)))
