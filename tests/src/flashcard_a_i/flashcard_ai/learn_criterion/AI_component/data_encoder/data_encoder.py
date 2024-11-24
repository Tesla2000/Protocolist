from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from collections.abc import Generator
from collections.abc import Iterable
from collections.abc import Iterator
from typing import Optional

from numpy import ndarray

from tests.src.flashcard_a_i.flashcard_ai.learn_criterion.AI_component.data_encoder.samples_divisor.samples_divisor import (  # noqa: E501
    SamplesDivisor,
)
from tests.src.flashcard_a_i.models.result import Result


class DataEncoder(ABC):
    def __init__(self, sample_divisor: SamplesDivisor):
        """
        Initializes the DataEncoder class with a specified SamplesDivisor
        instance.
        :param sample_divisor: An instance of SamplesDivisor used for dividing
        results into samples.
        :return: None
        """
        self.sample_divisor = sample_divisor

    def encode(
        self, results: Iterable[Result]
    ) -> Generator[tuple[ndarray, int], None, None]:
        """
        The `encode` function processes an iterable of `Result` objects,
        dividing them into samples and yielding encoded tuples of numpy arrays
        and integers by applying the `_encode_sample` method to each sample. It
        utilizes a generator to efficiently handle potentially large datasets.
        :param results: Yields encoded samples as tuples of numpy arrays and
        their corresponding integer labels by processing the provided iterable
        of results.
        :return: A generator yielding tuples of encoded samples and their
        corresponding indices.
        """
        yield from map(self._encode_sample, self._divide_to_samples(results))

    def _encode_sample(
        self, sample: Iterable[Optional[Result]]
    ) -> tuple[ndarray, int]:
        """
        The `_encode_sample` function takes an iterable of optional `Result`
        objects, extracts the last result to determine its correctness, and
        encodes the preceding results into a format suitable for processing,
        returning a tuple containing the encoded data and a binary indicator of
        correctness.
        :param sample: An iterable containing optional Result objects, where
        the last element indicates the correctness of the sample.
        :return: A tuple containing the encoded sample data and a binary
        indicator of correctness.
        """
        *previous_results, last_result = tuple(sample)
        y = int(last_result.is_correct)
        return self.encode_x_sample(previous_results), y

    @abstractmethod
    def encode_x_sample(self, sample: Iterable[Optional[Result]]) -> ndarray:
        """
        The `encode_x_sample` function is an abstract method that takes an
        iterable of optional `Result` objects as input and returns a NumPy
        ndarray, intended for encoding or transforming the provided samples
        into a specific numerical format. This method must be implemented by
        any subclass that inherits from the containing class.
        :param sample: An iterable collection of optional Result objects to be
        encoded.
        :return: A NumPy array representing the encoded features of the input
        sample.
        """

    def _divide_to_samples(
        self, results: Iterable[Result]
    ) -> Iterator[Iterator[Optional[Result]]]:
        """
        The `_divide_to_samples` function is an abstract method that takes an
        iterable of `Result` objects and returns an iterator of iterators, each
        containing optional `Result` objects. This method is intended to be
        implemented by subclasses to define how the results are grouped into
        samples.
        :param results: :param results: An iterable collection of Result
        objects to be divided into smaller sample groups.
        :return: An iterator of iterators containing optional Result objects
        grouped into samples.
        """
        return self.sample_divisor.divide(results)
