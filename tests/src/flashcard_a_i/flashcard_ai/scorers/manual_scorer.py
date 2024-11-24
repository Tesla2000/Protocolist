from __future__ import annotations

from tests.src.flashcard_a_i.flashcard_ai.scorers.scorer import Scorer


class ManualScorer(Scorer):
    def score(self, word: str, translation: str) -> bool:
        """
        The `score` function prompts the user to input a binary score (0 or 1)
        for a given word and its translation, returning `True` for a score of 1
        and `False` for a score of 0. It converts the input to an integer and
        then to a boolean value.
        :param translation: :param word: The word for which the score is being
        evaluated, prompting the user for a binary input indicating its
        correctness.
        :param word: A string representing a word that is being evaluated for
        its correctness in relation to a given translation.
        :return: True if the user inputs '1', False if '0'.
        """
        return bool(int(input(f"{word}: {translation} 0/1:")))
