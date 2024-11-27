from __future__ import annotations

from numpy import ndarray
from sklearn.metrics import balanced_accuracy_score

from tests.src.flashcard_a_i.flashcard_ai.learn_criterion.AI_component.AI_loop.AI_tester.statistic_calculator.statictic_calculator import (  # noqa: E501
    StatisticCalculator,
)


class BalancedAccuracyCalculator(StatisticCalculator):
    name: str = "Balanced Accuracy"

    def calculate(self, y_true: ndarray[int], y_pred: ndarray[int]):
        """
        Calculates the balanced accuracy score between the true labels and
        predicted labels.
        :param y_pred: An array of predicted labels.
        :param y_true: An array of true labels.
        :return: Balanced accuracy score as a float.
        """
        return balanced_accuracy_score(y_true, y_pred)
