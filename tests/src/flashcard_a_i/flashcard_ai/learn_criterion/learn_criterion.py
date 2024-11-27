from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from collections.abc import Iterator

from tests.src.flashcard_a_i.models.result import Result


class LearnCriterion(ABC):
    @abstractmethod
    def is_learned(self, word: str, results: Iterator[Result]) -> bool:
        """
        The `is_learned` function is an abstract method that determines whether
        a given word has been learned based on the provided results. It takes a
        string `word` and an iterator of `Result` objects as parameters and
        returns a boolean value.
        :param results: :param word: A string representing the word to be
        checked for learning status.
        :param word: A string representing the word to be checked for learning
        status within the provided results.
        :return: True if the word has been learned based on the results;
        otherwise, False.
        """
