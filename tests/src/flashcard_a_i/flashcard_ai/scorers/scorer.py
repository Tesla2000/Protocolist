from __future__ import annotations

from abc import ABC
from abc import abstractmethod


class Scorer(ABC):
    @abstractmethod
    def score(self, word: str, translation: str) -> bool:
        """
        The `score` function is an abstract method that evaluates the
        correctness of a given translation for a specified word, returning a
        boolean value indicating whether the translation is accurate. This
        method must be implemented by any subclass that inherits from the class
        containing this abstract method.
        :param translation: :param word: The input string that needs to be
        evaluated against the provided translation for scoring purposes.
        :param word: A string representing the word to be evaluated in relation
        to its translation.
        :return: A boolean indicating whether the translation of the word is
        correct.
        """
