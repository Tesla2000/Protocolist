from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from collections.abc import Iterable


class TrainFilter(ABC):

    @abstractmethod
    def filter_words(self, words: Iterable[str]) -> list[str]:
        """
        The `filter_words` function is an abstract method that, when
        implemented, is designed to take an iterable of strings as input and
        return a list of filtered words based on specific criteria defined in
        the subclass. This method enforces a contract for subclasses to provide
        their own filtering logic.
        :param words: An iterable collection of strings representing the words
        to be filtered by the function.
        :return: A list of filtered words based on specific criteria.
        """
