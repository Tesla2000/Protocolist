from __future__ import annotations

from typing import Protocol
from typing import runtime_checkable

from tests.src.flashcard_a_i.flashcard_ai.learn_criterion.AI_component.AI_loop.AI_models.ai_model import (  # noqa: E501
    AIModel,
)


@runtime_checkable
class SklearnModel(AIModel, Protocol):
    def fit(self, X, y):
        """
        The `fit` function is an abstract method intended to be implemented by
        subclasses for training a model using the input features `X` and target
        labels `y`. Currently, it raises a `NotImplementedError`, indicating
        that the method must be defined in a derived class.
        :param X: The parameter X represents the input features or data points
        used for training the model.
        :param y: The target variable or labels that the model aims to predict
        based on the input features X.
        :return: An error indicating the method is not implemented.
        """
        raise NotImplementedError
