from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from collections.abc import Sequence
from typing import Any

from numpy import ndarray

from tests.src.flashcard_a_i.flashcard_ai.learn_criterion.AI_component.AI_loop.AI_models.ai_model import (  # noqa: E501
    AIModel,
)
from tests.src.flashcard_a_i.flashcard_ai.learn_criterion.AI_component.AI_loop.AI_tester.statistic_calculator.statictic_calculator import (  # noqa: E501
    StatisticCalculator,
)


class AITester(ABC):
    def __init__(self, statistic_calculators: Sequence[StatisticCalculator]):
        """
        Initializes an AITester instance with a list of statistic calculators.
        :param statistic_calculators: A sequence of StatisticCalculator
        instances used for evaluating model predictions.
        :return: None
        """
        self.statistic_calculators = statistic_calculators

    @abstractmethod
    def _test(self, model: AIModel, X) -> ndarray[int]:
        """
        Abstract method for testing an AI model on given input data.
        :param model: An instance of AIModel to be tested.
        :param X: Input data for the model to make predictions on.
        :return: Array of predicted integer labels.
        """

    def test(self, model: AIModel, X, y) -> dict[str, Any]:
        """
        Tests the given AI model on the provided data and computes statistics
        using predefined calculators.
        :param model: An instance of AIModel to be tested.
        :param y: True labels for the input data.
        :param X: Input data for the model to make predictions.
        :return: A dictionary of calculated statistics.
        """
        y_pred = self._test(model, X)
        return {
            calculator.name: calculator.calculate(y, y_pred)
            for calculator in self.statistic_calculators
        }
