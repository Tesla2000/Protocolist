from __future__ import annotations

from collections.abc import Generator
from collections.abc import Sequence
from random import randint
from random import random

from tests.src.flashcard_a_i.flashcard_ai.word_picker.word_picker import (
    WordPicker,
)


class RandomPickDecorator(WordPicker):
    def __init__(
        self, word_picker: WordPicker, random_repetition_change: float = 0.05
    ):
        """
        Initializes a RandomPickDecorator instance that modifies word selection
        behavior based on a specified repetition change.
        :param random_repetition_change: A float that determines the
        probability of repeating a word during selection.
        :param word_picker: An instance of WordPicker used for selecting words.
        :return: None
        """
        super().__init__(word_picker.user)
        self.random_repetition_change = random_repetition_change
        self.word_picker = word_picker

    def pick(
        self, words: Sequence[str], translations: Sequence[str]
    ) -> Generator[tuple[str, str]]:
        """
        The `pick` function randomly selects a word from a given list of words
        that the user has not yet learned, yielding each selected word along
        with its corresponding translation until there are no unlearned words
        left. It utilizes a generator to provide pairs of words and
        translations on demand.
        :param words: A sequence of strings representing the words from which a
        random selection will be made for translation.
        :param translations: :param words: A sequence of words from which a
        random choice will be made, excluding those already learned.
        :return: A generator yielding tuples of words and their corresponding
        translations.
        """
        for word, translation in self.word_picker.pick(words, translations):
            if random() < self.random_repetition_change:
                random_index = randint(0, len(words) - 1)
                yield words[random_index], translations[random_index]
            yield word, translation
