from __future__ import annotations

from collections.abc import Iterable
from itertools import islice

from tests.src.flashcard_a_i.word_extraction.train_filter.train_filter import (
    TrainFilter,
)


class NFirstTrainFilter(TrainFilter):
    def __init__(self, limit: int):
        """
        The `__init__` function initializes an instance of a class by setting a
        `limit` attribute to the provided integer value. This attribute can be
        used later in the class to impose constraints or define behavior based
        on the specified limit.
        :param limit: An integer that specifies the maximum allowable value or
        threshold for the instance.
        :return: an integer representing the maximum allowable value
        """
        self.limit = limit

    def filter_words(self, words: Iterable[str]) -> list[str]:
        """
        The `filter_words` function takes an iterable of strings and returns a
        list containing up to a specified number of elements, determined by the
        `self.limit` attribute, using the `islice` function for efficient
        slicing.
        :param words: An iterable collection of strings that will be filtered
        based on a specified limit.
        :return: a list of the first 'limit' words from the input iterable
        """
        return list(islice(words, self.limit))
