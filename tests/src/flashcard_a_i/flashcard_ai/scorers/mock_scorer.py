from __future__ import annotations

from tests.src.flashcard_a_i.flashcard_ai.scorers.scorer import Scorer


class MockScorer(Scorer):
    def score(self, word: str, translation: str) -> bool:
        """
        The `score` function takes a word and its translation as input
        parameters, prints them, and always returns `True`. This function
        appears to be a placeholder or a debugging tool rather than a fully
        implemented scoring mechanism.
        :param translation: :param word: A string representing the word to be
        scored against the provided translation.
        :param word: A string representing a word that is to be scored against
        its translation.
        :return: True if the word and translation are valid, otherwise False.
        """
        print(word, translation)
        return True
