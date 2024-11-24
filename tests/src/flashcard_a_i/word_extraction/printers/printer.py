from __future__ import annotations

import json
from abc import ABC
from abc import abstractmethod
from typing import Any


class Printer(ABC):
    @abstractmethod
    def print(self, data: Any) -> None:
        """
        The `print` function is an abstract method that, when implemented, is
        intended to output the provided `data` of any type without returning a
        value. It serves as a blueprint for subclasses to define their own
        printing behavior.
        :param data: Represents the input data to be processed or displayed by
        the function.
        :return: None; this method is intended for outputting data without
        returning a value.
        """


class JsonPrinter(Printer):
    def __init__(self, indent: int = 2):
        """
        The `__init__` function initializes an instance of a class with a
        specified indentation level, defaulting to 2 if no value is provided.
        It sets the `indent` attribute to the given integer value.
        :param indent: Specifies the number of spaces used for indentation in
        the output, with a default value of 2.
        :return: The indentation level for formatting output.
        """
        self.indent = indent

    def print(self, data: dict) -> None:
        """
        The `print` function takes a dictionary as input and outputs its JSON
        representation with a specified indentation level, enhancing
        readability. It utilizes the `json.dumps` method to format the data
        before printing.
        :param data: A dictionary containing data to be formatted and printed
        as a JSON string.
        :return: Formatted JSON string of the input dictionary.
        """
        print(json.dumps(data, indent=self.indent))
