from __future__ import annotations

from collections.abc import Iterable
from itertools import islice

from tests.src.flashcard_a_i.flashcard_ai.learn_criterion.learn_criterion import (  # noqa: E501
    LearnCriterion,
)
from tests.src.flashcard_a_i.models.result import Result


class RecentTriesCriterion(LearnCriterion):
    def __init__(self, n_successes: int, n_tries: int):
        """
        The `__init__` function initializes an object with two attributes:
        `n_successes`, representing the number of successful outcomes, and
        `n_tries`, indicating the total number of attempts made. This
        constructor is typically used in classes that model probabilistic
        events or experiments.
        :param n_tries: The number of attempts made in an experiment or process
        to achieve a certain outcome.
        :param n_successes: An integer representing the number of successful
        outcomes in a series of trials.
        :return: The number of successes and tries for a statistical
        experiment.
        """
        self.n_successes = n_successes
        self.n_tries = n_tries

    def is_learned(self, word: str, results: Iterable[Result]) -> bool:
        """
        The `is_learned` function determines if a given word has been
        successfully learned based on the results of a specified number of
        attempts, checking if the count of correct results meets or exceeds a
        predefined success threshold. It evaluates the most recent attempts,
        sorting them by date and limiting the count to a specified number of
        tries.
        :param results: :param results: An iterable of Result objects that are
        sorted by date in descending order, where the function checks if the
        number of correct results in the most recent attempts meets or exceeds
        a specified threshold for success.
        :param word: A string representing a specific word for which the
        learning status is being evaluated based on the results of previous
        attempts.
        :return: A boolean indicating if the specified word has been
        successfully learned based on recent results.
        """
        return (
            sum(
                map(
                    lambda result: result.is_correct,
                    islice(
                        sorted(
                            results,
                            key=lambda result: result.date,
                            reverse=True,
                        ),
                        self.n_tries,
                    ),
                )
            )
            >= self.n_successes
        )
