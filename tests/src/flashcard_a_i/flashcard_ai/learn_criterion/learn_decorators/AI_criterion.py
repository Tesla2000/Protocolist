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


class AICriterionDecorator(LearnCriterion):
    def __init__(
        self,
        learn_criterion: LearnCriterion,
        encoder: DataEncoder,
        ai_model: AIModel,
        learn_threshold: float = 0.95,
    ):
        """
        Initializes an instance of the AICriterionDecorator class, which
        combines a learning criterion with an AI model and data encoder.
        :param ai_model: An instance of the AIModel used for predictions.
        :param learn_criterion: An instance of LearnCriterion that defines the
        learning criteria.
        :param encoder: An instance of DataEncoder responsible for encoding
        data.
        :param learn_threshold: A float value representing the threshold for
        learning, defaulting to 0.95.
        :return: None
        """
        self.learn_threshold = learn_threshold
        self.learn_criterion = learn_criterion
        self.encoder = encoder
        self.ai_model = ai_model

    def is_learned(self, word: str, results: Iterable[Result]) -> bool:
        """
        Determines if a given word has been learned based on previous results
        and a learning criterion.
        :param results: An iterable of results used to assess learning.
        :param word: The word to check for learning status.
        :return: True if learned, otherwise False.
        """
        previous_results = last(self.encoder.encode(results), None)
        if previous_results is None:
            return self.learn_criterion.is_learned(word, results)
        return self.ai_model.predict_proba(previous_results[0].reshape(1, -1))[
            0, -1
        ] >= self.learn_threshold or self.learn_criterion.is_learned(
            word, results
        )
