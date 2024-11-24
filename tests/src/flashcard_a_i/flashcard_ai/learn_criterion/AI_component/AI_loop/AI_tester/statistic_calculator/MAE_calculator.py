from __future__ import annotations

from numpy import ndarray
from sklearn.metrics import mean_absolute_error

from tests.src.flashcard_a_i.flashcard_ai.learn_criterion.AI_component.AI_loop.AI_tester.statistic_calculator.statictic_calculator import (  # noqa: E501
    StatisticCalculator,
)


class MAECalculator(StatisticCalculator):
    name: str = "Mean Absolute Error"

    def calculate(self, y_true: ndarray[int], y_pred: ndarray[int]):
        """
        Calculates the Mean Absolute Error (MAE) between the true and predicted
        values.
        :param y_true: An array of true values for comparison.
        :param y_pred: An array of predicted values, where the last column is
        used for MAE calculation.
        :return: Mean Absolute Error value
        """
        return mean_absolute_error(y_true, y_pred[:, -1])
