from __future__ import annotations

from tests.src.flashcard_a_i.flashcard_ai.scorers.scorer import Scorer


class ManualScorerHidden(Scorer):
    def score(self, word: str, translation: str) -> bool:
        """
        The `score` function prompts the user to input a response for a given
        word and checks if the input matches any of the provided translations
        (split by commas), returning `True` if there's a match and `False`
        otherwise. If the user's input does not match, it prints the available
        translations for reference.
        :param translation: :param translation: A comma-separated string of
        valid translations against which the user's input for the given word is
        checked for a match.
        :param word: A string representing the word to be scored against a list
        of possible translations.
        :return: True if the input matches a translation; otherwise, False.
        """
        result = input(f"{word}: ") in map(str.strip, translation.split(","))
        if not result:
            print(translation)
        return result
