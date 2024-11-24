from __future__ import annotations

from tests.src.flashcard_a_i.flashcard_ai.result_saver.saver import Saver
from tests.src.flashcard_a_i.flashcard_ai.scorers.scorer import Scorer
from tests.src.flashcard_a_i.flashcard_ai.word_picker.word_picker import (
    WordPicker,
)
from tests.src.flashcard_a_i.flashcard_ai.words_extractors.words_extractor import (  # noqa: E501
    WordsExtractor,
)


class Player:
    def __init__(
        self,
        saver: Saver,
        scorer: Scorer,
        word_picker: WordPicker,
        words_extractor: WordsExtractor,
    ):
        """
        The `__init__` function initializes an instance of a class by accepting
        four parameters: `saver`, `scorer`, `word_picker`, and
        `words_extractor`, which are assigned to instance variables for later
        use. This setup allows the class to utilize these components for its
        intended functionality.
        :param saver: :param saver: An object responsible for saving the state
        or results of the process.
        :param scorer: A scoring mechanism that evaluates the performance or
        quality of a given set of words or selections within the context of the
        function.
        :param words_extractor: A component responsible for extracting relevant
        words or phrases from a given text input for further processing or
        analysis.
        :param word_picker: A component responsible for selecting words based
        on specific criteria or strategies during the execution of the
        function.
        :return: An instance of the class initialized with the provided
        components for saving, scoring, word selection, and extraction.
        """
        self.saver = saver
        self.scorer = scorer
        self.word_picker = word_picker
        self.words_extractor = words_extractor

    def play_round(self):
        """
        The `play_round` function extracts a list of words and their
        translations, selects one pair at random, and then updates the score
        based on the chosen word and its translation.
        :return: The score for the selected word and its translation.
        """
        words, translations = self.words_extractor.extract()
        word, translation = next(self.word_picker.pick(words, translations))
        self._score(word, translation)

    def play_till_learned(self):
        """
        The `play_till_learned` function extracts a list of words and their
        translations, then iteratively selects and scores each word-translation
        pair until the learning objective is achieved.
        :return: A score reflecting the user's learning progress with selected
        words and translations.
        """
        words, translations = self.words_extractor.extract()
        for word, translation in self.word_picker.pick(words, translations):
            self._score(word, translation)

    def _score(self, word: str, translation: str):
        """
        The `_score` function calculates a score for a given word and its
        translation using a scoring method, then saves the word, translation,
        and resulting score.
        :param translation: :param translation: The translated version of the
        input word used to evaluate its scoring against the original word.
        :param word: A string representing the word to be scored and saved
        alongside its translation.
        :return: The score of the word based on its translation.
        """
        result = self.scorer.score(word, translation)
        self.saver.save(word, translation, result)
