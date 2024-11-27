from __future__ import annotations

from pathlib import Path
from typing import List


class WikiWordsProcessor:

    def __init__(self, file_path: str = "app/wiki-100k.txt"):
        """
        The `__init__` function initializes an instance by setting the file
        path to a specified text file (defaulting to "app/wiki-100k.txt") and
        extracts words from that file for further processing.
        :param file_path: Specifies the path to the text file containing words
        to be extracted, defaulting to "app/wiki-100k.txt".
        :return: A list of words extracted from the specified text file.
        """
        self.file_path = Path(file_path)
        self.words = self._extract_words()

    def _extract_words(self) -> List[str]:
        """
        The `_extract_words` function reads the content of a file specified by
        `self.file_path` and splits the text into a list of individual words.
        It returns this list of words as a `List[str]`.
        :return: A list of words extracted from the file's text.
        """
        return self.file_path.read_text().split()

    def _filter_words(self, word_list: List[str]) -> List[str]:
        """
        The `_filter_words` function takes a list of words and returns a new
        list containing only those words that are present in the object's
        `words` attribute. It effectively filters out any words not found in
        the specified collection.
        :param word_list: A list of strings representing words to be filtered
        based on their presence in a predefined set of valid words.
        :return: A filtered list of words present in the file.
        """
        return [word for word in word_list if word in self.words]

    def _find_word_position(self, word: str) -> int:
        """
        The `_find_word_position` function searches for the specified `word` in
        the `self.words` list and returns its index. If the word is not found,
        it will raise a `ValueError`.
        :param word: A string representing the word whose position is to be
        found in the list of words.
        :return: The index of the specified word in the list.
        """
        return self.words.index(word)

    def sort_words_by_position_desc(self, word_list: List[str]) -> List[str]:
        """
        The `sort_words_by_position_desc` function filters a list of words and
        then sorts the filtered words in descending order based on their
        positions, as determined by the `_find_word_position` method. It
        returns the sorted list of words.
        :param word_list: A list of strings representing words that will be
        filtered and sorted based on their positional values in descending
        order.
        :return: A list of filtered words sorted by their position in
        descending order.
        """
        filtered_words = self._filter_words(word_list)
        return sorted(
            filtered_words, key=self._find_word_position, reverse=True
        )
