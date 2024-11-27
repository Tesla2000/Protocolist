from __future__ import annotations

from collections.abc import Iterable
from itertools import chain
from operator import attrgetter

from more_itertools import map_reduce
from more_itertools import unzip
from numpy import ndarray
from numpy.ma.core import array

from tests.src.flashcard_a_i.flashcard_ai.learn_criterion.AI_component.data_creator.data_creator import (  # noqa: E501
    DataCreator,
)
from tests.src.flashcard_a_i.flashcard_ai.learn_criterion.AI_component.data_creator.results_getter.results_getter import (  # noqa: E501
    ResultsGetter,
)
from tests.src.flashcard_a_i.flashcard_ai.learn_criterion.AI_component.data_encoder.data_encoder import (  # noqa: E501
    DataEncoder,
)
from tests.src.flashcard_a_i.models.result import Result


class RecentlyLearnedDataCreator(DataCreator):
    def __init__(
        self,
        data_encoder: DataEncoder,
        results_getter: ResultsGetter,
        include_translations: bool = False,
    ):
        """
        Initializes the RecentlyLearnedDataCreator with a specified data
        encoder and an option to include translations.
        :param data_encoder: An instance of DataEncoder used for encoding data.
        :param include_translations: A boolean flag indicating whether to
        include translations in the data processing.
        :return: None
        """
        super().__init__(data_encoder)
        self.include_translations = include_translations
        self.results_getter = results_getter

    def create_data(self):
        """
        The `create_data` function generates a sequence of tuples containing
        user identifiers and their corresponding data arrays by aggregating
        results from a database query, converting them into a specific format.
        It utilizes a map-reduce approach to group results by user and
        processes each group into arrays for further use.
        :return: A generator yielding tuples of user, x array, and y array from
        aggregated results.
        """
        for user, results in map_reduce(
            self.results_getter.get_results(), attrgetter("user")
        ).items():
            x, y = self._conv_to_array(results)
            yield user, x, y

    def _conv_to_array(
        self, results: Iterable[Result]
    ) -> tuple[ndarray[ndarray[int]], ndarray[ndarray[int]]]:
        """
        The `_conv_to_array` function processes an iterable of `Result`
        objects, grouping them by their `word` and `translation` attributes,
        and then encodes these groups into two NumPy arrays. It returns a tuple
        containing these arrays, which represent the encoded data for further
        analysis or processing.
        :param results: This function processes a collection of
        Result objects to create two numpy arrays, one for encoded input data
        and another for corresponding encoded output data, based on unique
        words and their translations.
        :return: A tuple containing two numpy arrays representing encoded
        attempts and their corresponding translations.
        """
        attempts = {}
        for result in results:
            attempts[result.word] = attempts.get(result.word, []) + [result]
            if self.include_translations:
                attempts[result.translation] = attempts.get(
                    result.translation, []
                ) + [result]
        x_y_generators = map(self.data_encoder.encode, attempts.values())
        x_y_arrays = unzip(chain.from_iterable(x_y_generators))
        return tuple(map(array, map(tuple, x_y_arrays)))
