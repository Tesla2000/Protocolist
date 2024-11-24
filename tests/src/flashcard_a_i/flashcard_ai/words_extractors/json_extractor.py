from __future__ import annotations

import json
from pathlib import Path

from tests.src.flashcard_a_i.flashcard_ai.words_extractors.words_extractor import (  # noqa: E501
    WordsExtractor,
)


class JsonWordsExtractor(WordsExtractor):
    def __init__(self, path: Path | str):
        """
        This function initializes an object by accepting a file path, reading
        its contents as text, and parsing it as JSON to extract keys and values
        into separate lists for words and their translations.
        :param path: Specifies the file path as either a string or a Path
        object from which to read and parse JSON content.
        :return: A list of translation keys and their corresponding values from
        a JSON file.
        """
        self.path = Path(path)
        self.contents = self.path.read_text()
        self.json = json.loads(self.contents)
        self.words = list(self.json.keys())
        self.translations = list(self.json.values())

    def extract(self) -> tuple[list[str], list[str]]:
        """
        The `extract` function returns a tuple containing two lists: one with
        words and the other with their corresponding translations. This allows
        for easy access to both sets of data stored within the object.
        :return: A tuple containing two lists: one of words and one of their
        translations.
        """
        return self.words, self.translations
