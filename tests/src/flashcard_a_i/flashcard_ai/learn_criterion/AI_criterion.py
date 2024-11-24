from __future__ import annotations

from collections.abc import Iterable

from more_itertools import last

from tests.src.flashcard_a_i.flashcard_ai.learn_criterion.AI_component.AI_loop.AI_models.ai_model import (  # noqa: E501
    AIModel,
)
from tests.src.flashcard_a_i.flashcard_ai.learn_criterion.AI_component.data_encoder.data_encoder import (  # noqa: E501
    DataEncoder,
)
from tests.src.flashcard_a_i.flashcard_ai.learn_criterion.learn_criterion import (  # noqa: E501
    LearnCriterion,
)
from tests.src.flashcard_a_i.models.result import Result


class AICriterion(LearnCriterion):
    def __init__(self, encoder: DataEncoder, ai_model: AIModel):
        """
        Initializes an instance of the AICriterion class with a specified data
        encoder and AI model.
        :param encoder: An instance of DataEncoder used for encoding data.
        :param ai_model: An instance of AIModel used for making predictions.
        :return: None
        """
        self.encoder = encoder
        self.ai_model = ai_model

    def is_learned(self, word: str, results: Iterable[Result]) -> bool:
        """
        Determines if a specific word has been learned based on the results
        provided and the AI model's predictions.
        :param word: The word to check if it has been learned.
        :param results: An iterable of results used for encoding and
        prediction.
        :return: True if learned, otherwise False
        """
        return (
            self.ai_model.predict_proba(last(self.encoder.encode(results))[0])[
                0, -1
            ]
            == 1
        )
