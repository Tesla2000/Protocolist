from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime

from tests.src.flashcard_a_i.flashcard_ai.learn_criterion.learn_criterion import (  # noqa: E501
    LearnCriterion,
)
from tests.src.flashcard_a_i.models.result import Result


class TimeFilter(LearnCriterion):
    def __init__(self, learn_criterion: LearnCriterion):
        """
        The `__init__` function initializes an instance of a class by setting a
        learning criterion and recording the current date and time as the start
        time. It takes a parameter `learn_criterion` of type `LearnCriterion`
        to define the learning criteria for the instance.
        :param learn_criterion: Specifies the criterion used for learning,
        which guides the optimization process during model training.
        :return: The initialization sets the learning criterion and records the
        start time.
        """
        self.learn_criterion = learn_criterion
        self.start_time = datetime.now()

    def is_learned(self, word: str, results: Iterator[Result]) -> bool:
        """
        The `is_learned` function checks if a specified word has been learned
        based on a set of results filtered by a defined start time, using a
        learning criterion. It returns a boolean indicating whether the word
        meets the learning criteria after filtering the results.
        :param word: A string representing the word to be evaluated against the
        learning criteria based on the provided results.
        :param results: :param results: An iterator of Result objects that are
        filtered to include only those with a date later than the instance's
        start_time, used to determine if the specified word meets the learning
        criterion.
        :return: True if the word has been learned based on recent results;
        otherwise, False.
        """
        filtered_results = filter(
            lambda result: result.date > self.start_time, results
        )
        return self.learn_criterion.is_learned(word, filtered_results)
