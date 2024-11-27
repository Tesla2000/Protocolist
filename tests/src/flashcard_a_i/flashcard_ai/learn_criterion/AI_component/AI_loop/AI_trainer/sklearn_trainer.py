from __future__ import annotations

from tests.src.flashcard_a_i.flashcard_ai.learn_criterion.AI_component.AI_loop.AI_models.ai_model import (  # noqa: E501
    AIModel,
)
from tests.src.flashcard_a_i.flashcard_ai.learn_criterion.AI_component.AI_loop.AI_models.sklearn_model import (  # noqa: E501
    SklearnModel,
)
from tests.src.flashcard_a_i.flashcard_ai.learn_criterion.AI_component.AI_loop.AI_trainer.ai_trainer import (  # noqa: E501
    AITrainer,
)


class SklearnTrainer(AITrainer):
    def __init__(self, sklearn_model: SklearnModel):
        """
        The `__init__` function initializes an instance of a class by accepting
        a parameter `sklearn_model`, ensuring it is an instance of
        `SklearnModel`; if not, it raises a `ValueError`. This constructor
        stores the validated model as an instance attribute for further use.
        :param sklearn_model: An instance of a scikit-learn model that will be
        used for training or predictions within the class.
        :return: An initialized instance of the class with a valid
        SklearnModel.
        """
        if not isinstance(sklearn_model, SklearnModel):
            raise ValueError
        self.sklearn_model = sklearn_model

    def train(self, X, y) -> AIModel:
        """
        The `train` function fits a scikit-learn model to the provided feature
        matrix `X` and target vector `y`, and raises a ValueError if the model
        is not an instance of `AIModel`. It returns the trained model upon
        successful fitting.
        :param y: The parameter y represents the target variable or labels
        corresponding to the input features X used for training the model.
        :param X: A dataset containing features used for training the machine
        learning model.
        :return: An instance of the trained AIModel.
        """
        self.sklearn_model.fit(X, y)
        if not isinstance(self.sklearn_model, AIModel):
            raise ValueError
        return self.sklearn_model
