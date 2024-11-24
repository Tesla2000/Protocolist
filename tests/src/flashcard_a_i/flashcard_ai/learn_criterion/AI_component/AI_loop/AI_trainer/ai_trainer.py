from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from tests.src.flashcard_a_i.flashcard_ai.learn_criterion.AI_component.AI_loop.AI_models.ai_model import (  # noqa: E501
    AIModel,
)


class AITrainer(ABC):
    @abstractmethod
    def train(self, X, y) -> AIModel:
        """
        The `train` function is an abstract method that, when implemented, is
        intended to train an AI model using the provided input data `X` and
        corresponding labels `y`, returning an instance of the trained AI
        model.
        :param y: Represents the target values or labels corresponding to the
        input data X used for training the AI model.
        :param X: Represents the input features or data used for training the
        AI model.
        :return: An instance of an AIModel trained on the provided data.
        """
