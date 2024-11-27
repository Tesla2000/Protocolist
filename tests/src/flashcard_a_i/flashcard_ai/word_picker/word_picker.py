from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from collections.abc import Generator
from collections.abc import Iterable

from tests.src.flashcard_a_i.models.user import User


class WordPicker(ABC):
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
    def pick(
        self, words: Iterable[str], translations: Iterable[str]
    ) -> Generator[tuple[str, str]]:
        """
        The `pick` function is an abstract method that takes two iterable
        inputs, `words` and `translations`, and returns a generator yielding
        tuples of corresponding word-translation pairs. This method must be
        implemented by subclasses to define specific logic for pairing words
        with their translations.
        :param translations: :param words: An iterable collection of strings
        representing the words to be processed.
        :param words: A collection of strings representing the words to be
        translated.
        :return: A generator yielding pairs of words and their corresponding
        translations.
        """
