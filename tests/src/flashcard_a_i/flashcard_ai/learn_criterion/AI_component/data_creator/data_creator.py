from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from itertools import chain

from more_itertools import unzip
from numpy import array
from numpy import ndarray

from tests.src.flashcard_a_i.flashcard_ai.learn_criterion.AI_component.data_encoder.data_encoder import (  # noqa: E501
    DataEncoder,
)


class DataCreator(ABC):
    def __init__(self, data_encoder: DataEncoder):
        """
        The `__init__` function initializes an instance of a class by accepting
        a `DataEncoder` object as a parameter and assigns it to the instance
        variable `data_encoder`. This setup allows the class to utilize the
        functionality provided by the `DataEncoder` for further processing.
        :param data_encoder: An instance of the DataEncoder class used for
        encoding and processing data within the function.
        :return: an instance of the class initialized with a DataEncoder
        object.
        """
        self.data_encoder = data_encoder

    @abstractmethod
    def create_data(self):
        """
        The `create_data` function is an abstract method that must be
        implemented by any subclass, serving as a blueprint for generating or
        initializing data. It does not contain any implementation details, as
        indicated by the use of `pass`.
        :return: An instance of generated data based on specific criteria.
        """

    def create_data_combined(self) -> ndarray:
        """
        Combines and transforms data generated by the `create_data` method into
        a structured format.
        :return: A tuple of arrays containing the combined data.
        """
        all_data = map(chain.from_iterable, unzip(self.create_data())[-2:])
        return tuple(map(array, map(tuple, all_data)))
