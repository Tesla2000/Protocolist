from __future__ import annotations

from collections.abc import Iterable
from typing import Optional

from tests.src.flashcard_a_i.flashcard_ai.learn_criterion.AI_component.data_creator.results_getter.results_getter import (  # noqa: E501
    ResultsGetter,
)
from tests.src.flashcard_a_i.models.result import Result
from tests.src.flashcard_a_i.models.user import User


class UserFilteredResults(ResultsGetter):
    def __init__(self, user: Optional[User] = None):
        self.user = user

    def get_results(self) -> Iterable[Result]:
        if self.user is None:
            return Result.select()
        return Result.select().where(Result.user == self.user)
