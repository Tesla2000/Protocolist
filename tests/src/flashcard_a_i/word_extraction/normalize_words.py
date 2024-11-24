from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from collections.abc import Iterable


class SequenceNormalizerStrategy(ABC):
    @abstractmethod
    def normalize(self, word: Iterable[str]) -> list[str]:
        """
        The `normalize` function is an abstract method that takes an iterable
        of strings as input and returns a list of normalized strings. It is
        intended to be implemented by subclasses to define specific
        normalization behavior for the provided words.
        :param word: An iterable collection of strings that represents the
        words to be normalized.
        :return: A list of normalized strings.
        """


class TrimAndLowercaseNormalizer(SequenceNormalizerStrategy):
    def normalize(self, sequence: Iterable[str]) -> set[str]:
        """
        The `normalize` function takes an iterable of strings and returns a set
        of unique, lowercase words that contain only alphabetic characters,
        after stripping any leading or trailing whitespace.
        :param sequence: A sequence of strings that will be processed to return
        a set of unique, lowercase words containing only alphabetic characters,
        with leading and trailing whitespace removed.
        :return: a set of unique, lowercase alphabetic words
        """
        return set(word.lower().strip() for word in sequence if word.isalpha())


def word_normalizer_decorator(strategy: SequenceNormalizerStrategy):
    """
    The `word_normalizer_decorator` is a decorator that applies a specified
    normalization strategy to the output of a decorated function, ensuring that
    the result is an iterable. If the output is not an iterable, it raises a
    ValueError, indicating that the function's output must be a list of words.
    :param strategy: :param strategy: A strategy object that defines the
    normalization process for the output of the decorated function, ensuring it
    is transformed into a standardized format.
    :return: A normalized list of words based on the provided strategy.
    """

    def decorator(func):
        """
        The `decorator` function is a higher-order function that wraps another
        function, checking if its output is an iterable; if so, it normalizes
        the result using a `strategy` method, otherwise, it raises a ValueError
        indicating that the output must be a list of words.
        :param func: A function that will be wrapped to ensure its output is an
        iterable, which is then normalized by a strategy if valid, or raises a
        ValueError if not.
        :return: normalized iterable or raises ValueError
        """

        def wrapper(*args, **kwargs):
            """
            The `wrapper` function calls a specified function (`func`) with any
            provided arguments and keyword arguments, normalizing the result if
            it is an iterable. If the result is not an iterable, it raises a
            ValueError indicating that the output must be a list of words.
            :return: normalized iterable or raises ValueError
            """
            result = func(*args, **kwargs)
            if isinstance(result, Iterable):
                return strategy.normalize(result)
            raise ValueError("Function output must be a list of words")

        return wrapper

    return decorator
