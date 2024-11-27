from __future__ import annotations

import random
from collections.abc import Generator
from collections.abc import Sequence
from operator import attrgetter
from operator import itemgetter
from pathlib import Path

from joblib import load
from more_itertools import map_reduce

from tests.src.flashcard_a_i.flashcard_ai.learn_criterion.AI_component.data_creator.data_creator import (  # noqa: E501
    DataCreator,
)
from tests.src.flashcard_a_i.flashcard_ai.learn_criterion.learn_criterion import (  # noqa: E501
    LearnCriterion,
)
from tests.src.flashcard_a_i.flashcard_ai.word_picker.word_picker import (
    WordPicker,
)
from tests.src.flashcard_a_i.models.user import User
from tests.src.flashcard_a_i.services.user import UserService


class AIRandomPicker(WordPicker):
    def __init__(
        self,
        user: User,
        learn_criterion: LearnCriterion,
        model_path: Path,
        data_creator: DataCreator,
    ):
        """
        The `__init__` function initializes an instance of a class by calling
        the parent class's initializer with a `User` object and setting a
        learning criterion using the provided `LearnCriterion` parameter.
        :param user: An instance of the User class representing the individual
        whose learning progress or behavior is being tracked or analyzed.
        :param learn_criterion: Specifies the criterion used for learning,
        which guides the model's training process and influences its
        performance.
        :return: An instance of the class initialized with a user and a
        learning criterion.
        """
        super().__init__(user)
        self.data_creator = data_creator
        self.model_path = model_path
        self.learn_criterion = learn_criterion
        self.model = load(self.model_path)

    def pick(
        self, words: Sequence[str], translations: Sequence[str]
    ) -> Generator[tuple[str, str]]:
        """
        The `pick` function randomly selects a word from a given list of words
        that the user has not yet learned, yielding each selected word along
        with its corresponding translation until there are no unlearned words
        left. It utilizes a generator to provide pairs of words and
        translations on demand.
        :param words: A sequence of strings representing the words from which a
        random selection will be made for translation.
        :param translations: :param words: A sequence of words from which a
        random choice will be made, excluding those already learned.
        :return: A generator yielding tuples of words and their corresponding
        translations.
        """
        while True:
            learned = self._get_learned_words()
            choices = tuple(set(words) - learned)
            # {
            #     choice: self.model.predict_proba(x[-1:])[0, 1]
            #     for _, x, _ in next(self.data_creator.create_data(choice))
            #     for choice in choices
            # }
            print(f"{len(choices)} left {choices=}")
            if not choices:
                return
            word = random.choice(choices)
            yield word, translations[words.index(word)]

    def _get_learned_words(self) -> set[str]:
        """
        The `_get_learned_words` function retrieves a set of words that the
        user has not yet learned by filtering and grouping the user's results
        based on a specified learning criterion. It utilizes sorting and
        grouping operations to efficiently identify and return the relevant
        words.
        :return: A set of words that have not been learned according to the
        specified learning criterion.
        """
        word_getter = attrgetter("word")
        results = UserService.get_results(self.user)
        results_divided_by_word = map_reduce(results, word_getter)
        learned_results = filter(
            lambda item: self.learn_criterion.is_learned(*item),
            results_divided_by_word.items(),
        )
        learned_words = map(itemgetter(0), learned_results)
        learned_words = set(learned_words)
        return learned_words
