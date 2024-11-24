from __future__ import annotations

from collections.abc import Iterator
from random import random

from tests.src.flashcard_a_i.flashcard_ai.learn_criterion.learn_criterion import (  # noqa: E501
    LearnCriterion,
)
from tests.src.flashcard_a_i.models.result import Result


class Randomize(LearnCriterion):
    def __init__(
        self,
        learn_criterion: LearnCriterion,
        random_repetition_change: float = 0.05,
    ):
        """
        The `__init__` function initializes an instance of a class, setting the
        learning criterion and a parameter for random repetition change, with a
        default value of 0.1. It takes two arguments: `learn_criterion`, which
        specifies the criterion for learning, and `random_repetition_change`,
        which controls the variability in repetition during the learning
        process.
        :param random_repetition_change: A float representing the probability
        of introducing random changes in repetition during the learning
        process, with a default value of 0.1.
        :param learn_criterion: Specifies the criterion used for learning,
        which guides the optimization process in the model.
        :return: An instance of the class initialized with a learning criterion
        and a random repetition change value.
        """
        self.learn_criterion = learn_criterion
        self.random_repetition_change = random_repetition_change

    def is_learned(self, word: str, results: Iterator[Result]) -> bool:
        """
        The `is_learned` function determines if a given word has been learned
        based on a random threshold and a specified learning criterion, using
        the results of previous attempts. It returns `True` if the word is
        considered learned, otherwise `False`.
        :param results: :param results: An iterator of Result objects that
        provide data used to determine if the specified word has been learned
        based on the defined learning criterion and a random threshold.
        :param word: A string representing the word for which the learning
        status is being evaluated based on specified criteria and results.
        :return: True if the word is considered learned based on criteria and
        randomness; otherwise, False.
        """
        return (
            random() > self.random_repetition_change
            and self.learn_criterion.is_learned(word, results)
        )
