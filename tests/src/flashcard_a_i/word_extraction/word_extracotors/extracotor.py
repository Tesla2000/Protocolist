from __future__ import annotations

from abc import ABC
from abc import abstractmethod


class WordExtractor(ABC):
    @staticmethod
    @abstractmethod
    def extract(file_path: str) -> set[str]:
        """
        The `extract` function is a static abstract method that, when
        implemented, is designed to take a file path as input and return a set
        of strings extracted from the specified file. This method serves as a
        blueprint for subclasses to define their own extraction logic.
        :param file_path: A string representing the path to the file from which
        data will be extracted.
        :return: A set of unique strings extracted from the specified file.
        """
