from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from tests.src.flashcard_a_i.models.result import Result
from tests.src.flashcard_a_i.models.user import User


class Saver(ABC):
    def __init__(self, user: User):
        """
        The `__init__` function initializes an instance of a class by accepting
        a `User` object and assigning it to the instance variable `self.user`.
        This allows the class to store and utilize the provided user
        information throughout its methods.
        :param user: An instance of the User class representing the individual
        associated with this object.
        :return: The initialized user object.
        """
        self.user = user

    @abstractmethod
    def save(self, word: str, translation: str, result: bool):
        """
        The `save` function is an abstract method that requires implementation
        in subclasses, designed to store a word, its translation, and a boolean
        result indicating success or failure. It takes three parameters: a
        string `word`, a string `translation`, and a boolean `result`.
        :param result: Indicates whether the save operation was successful or
        not.
        :param translation: :param word: The original word to be saved. :param
        result: A boolean indicating whether the save operation was successful
        or not.
        :param word: The parameter represents the word to be translated.
        :return: A boolean indicating the success of the save operation.
        """

    def _save_result(self, result: Result):
        """
        The `_save_result` function saves a given `Result` object by calling
        its `save` method. This function is likely part of a class that manages
        the storage of results.
        :param result: An instance of the Result class that contains data to be
        saved.
        :return: the result is saved to persistent storage.
        """
        result.save()
