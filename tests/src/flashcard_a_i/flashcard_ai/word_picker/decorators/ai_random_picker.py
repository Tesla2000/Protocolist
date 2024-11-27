from __future__ import annotations

from collections.abc import Generator
from collections.abc import Sequence
from pathlib import Path
from random import choices
from random import random

import numpy as np
from joblib import load

from tests.src.flashcard_a_i.flashcard_ai.learn_criterion.AI_component.data_creator.data_creator import (  # noqa: E501
    DataCreator,
)
from tests.src.flashcard_a_i.flashcard_ai.word_picker.word_picker import (
    WordPicker,
)


class AIRandomPickDecorator(WordPicker):
    def __init__(
        self,
        word_picker: WordPicker,
        model_path: Path,
        data_creator: DataCreator,
        random_repetition_change: float = 0.05,
        randomness_factor: float = 3,
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
        self.randomness_factor = randomness_factor
        self.data_creator = data_creator
        self.model_path = model_path
        self.random_repetition_change = random_repetition_change
        self.word_picker = word_picker
        self.model = load(self.model_path)

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
                word_samples = {
                    word: x[-1]
                    for word, x, y in self.data_creator.create_data()
                }
                word_odds = dict(
                    zip(
                        word_samples.keys(),
                        self.model.predict_proba(
                            np.array(tuple(word_samples.values()))
                        )[:, 1],
                    )
                )
                picked_word = None
                while picked_word not in words:
                    picked_word = choices(
                        tuple(word_odds.keys()),
                        tuple(
                            self.randomness_factor - word_odds[word]
                            for word in word_odds.keys()
                        ),
                        k=1,
                    )[0]
                picked_word_index = words.index(picked_word)
                yield words[picked_word_index], translations[picked_word_index]
            yield word, translation
