from __future__ import annotations

from numpy import ndarray

from tests.src.flashcard_a_i.flashcard_ai.learn_criterion.AI_component.AI_loop.AI_models.sklearn_model import (  # noqa: E501
    SklearnModel,
)
from tests.src.flashcard_a_i.flashcard_ai.learn_criterion.AI_component.AI_loop.AI_tester.ai_tester import (  # noqa: E501
    AITester,
)


class SklearnTester(AITester):
    def _test(self, model: SklearnModel, X) -> ndarray[int]:
        """
        Tests the provided scikit-learn model by predicting probabilities for
        the given feature matrix.
        :param model: The model parameter is expected to be an instance of
        SklearnModel.
        :param X: A dataset containing features used for training the machine
        learning model.
        :return: Predicted probabilities as an ndarray of integers.
        """

        if not isinstance(model, SklearnModel):
            raise ValueError
        return model.predict_proba(X)
