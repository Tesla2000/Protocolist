from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from numpy import ndarray


class StatisticCalculator(ABC):
    name: str

    @abstractmethod
    def calculate(self, y_true: ndarray[int], y_pred: ndarray[int]):
        """
        Calculates a statistical metric based on the true and predicted values.
        :param y_pred: An array of predicted integer values.
        :param y_true: An array of true integer values.
        :return: Statistical metric result.
        """
