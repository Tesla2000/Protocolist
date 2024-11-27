from __future__ import annotations

from collections.abc import Sequence

from tests.src.flashcard_a_i.flashcard_ai.learn_criterion.learn_criterion import (  # noqa: E501
    LearnCriterion,
)
from tests.src.flashcard_a_i.models.result import Result


class OrDecorator(LearnCriterion):
    def __init__(
        self,
        learn_criterion1: LearnCriterion,
        learn_criterion2: LearnCriterion,
    ):
        """
        Initializes an OrDecorator instance with two learning criteria.
        :param learn_criterion1: The first learning criterion to evaluate.
        :param learn_criterion2: The second learning criterion to evaluate.
        :return: None
        """
        self.learn_criterion1 = learn_criterion1
        self.learn_criterion2 = learn_criterion2

    def is_learned(self, word: str, results: Sequence[Result]) -> bool:
        """
        Determines if a word is learned based on two learning criteria.
        :param word: The word to check for learning status.
        :param results: A sequence of results associated with the learning
        process.
        :return: True if learned, otherwise False.
        """
        return self.learn_criterion1.is_learned(
            word, results
        ) or self.learn_criterion2.is_learned(word, results)
