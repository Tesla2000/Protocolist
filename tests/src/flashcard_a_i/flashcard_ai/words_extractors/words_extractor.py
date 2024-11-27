from __future__ import annotations

from abc import ABC
from abc import abstractmethod


class WordsExtractor(ABC):
    @abstractmethod
    def extract(self) -> tuple[list[str], list[str]]:
        """
        The `extract` function is an abstract method that, when implemented, is
        expected to return a tuple containing two lists of strings. This method
        serves as a blueprint for subclasses to define their own extraction
        logic.
        :return: A tuple containing two lists of strings.
        """
