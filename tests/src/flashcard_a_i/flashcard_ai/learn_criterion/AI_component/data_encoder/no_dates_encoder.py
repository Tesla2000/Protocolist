from __future__ import annotations

from collections.abc import Iterable
from typing import Optional

from numpy import array
from numpy import ndarray

from tests.src.flashcard_a_i.flashcard_ai.learn_criterion.AI_component.data_encoder.data_encoder import (  # noqa: E501
    DataEncoder,
)
from tests.src.flashcard_a_i.models.result import Result


class NoDatesEncoder(DataEncoder):
    def encode_x_sample(
        self, sample: Iterable[Optional[Result]]
    ) -> tuple[ndarray, int]:
        """
        Encodes a sample of results into a binary format, returning a NumPy
        array and its length.
        :param sample: An iterable containing optional Result objects.
        :return: A tuple containing a NumPy array and an integer.
        """
        encoded = map(int, map(bool, sample))
        return array(tuple(encoded))
