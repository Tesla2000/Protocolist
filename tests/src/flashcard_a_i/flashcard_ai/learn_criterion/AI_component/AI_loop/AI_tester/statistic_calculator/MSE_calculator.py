from __future__ import annotations

from numpy import ndarray
from sklearn.metrics import mean_squared_error

from tests.src.flashcard_a_i.flashcard_ai.learn_criterion.AI_component.AI_loop.AI_tester.statistic_calculator.statictic_calculator import (  # noqa: E501
    StatisticCalculator,
)


class MSECalculator(StatisticCalculator):
    name: str = "Mean Squared Error"

    def calculate(self, y_true: ndarray[int], y_pred: ndarray[int]):
        """
        Calculates the Mean Squared Error (MSE) between the true values and the
        predicted values from the last column of the predictions array.
        :param y_pred: An array of predicted values, where the last column is
        used for MSE calculation.
        :param y_true: An array of true values to compare against the
        predictions.
        :return: Mean Squared Error value
        """
        return mean_squared_error(y_true, y_pred[:, -1])
