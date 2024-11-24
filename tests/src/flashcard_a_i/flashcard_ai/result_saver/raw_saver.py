from __future__ import annotations

from tests.src.flashcard_a_i.flashcard_ai.result_saver.saver import Saver
from tests.src.flashcard_a_i.models.result import Result


class RawSaver(Saver):
    def save(self, word: str, translation: str, result: bool):
        """
        The `save` function creates a `Result` object with the specified word,
        translation, and correctness status, then saves it using the
        `_save_result` method.
        :param translation: :param word: The word to be saved alongside its
        translation. :param result: A boolean indicating whether the
        translation was correct or not.
        :param result: Indicates whether the user's translation of the word is
        correct or not.
        :param word: A string representing the word to be translated.
        :return: A Result object containing user, word, translation, and
        correctness status.
        """
        result = Result(
            user=self.user,
            word=word,
            translation=translation,
            is_correct=result,
        )
        self._save_result(result)
