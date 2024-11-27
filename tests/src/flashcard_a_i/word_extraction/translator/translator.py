from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import List

import requests


class Translator(ABC):

    def translate(
        self, texts: Iterable[str], target_language: str
    ) -> List[str]:
        """
        The `translate` function takes an iterable of text strings and a target
        language as input, and returns a list of translated texts by applying a
        translation method to each text. It utilizes the `map` function along
        with `partial` to streamline the translation process for the specified
        target language.
        :param target_language: Specifies the language into which the provided
        texts will be translated.
        :param texts: An iterable collection of strings that are to be
        translated into the specified target language.
        :return: A list of translated strings in the specified target language.
        """
        return list(
            map(
                partial(self._translate, target_language=target_language),
                texts,
            )
        )

    @abstractmethod
    def _translate(self, texts: str, target_language: str) -> str:
        """
        The `_translate` function is an abstract method that, when implemented,
        is designed to take a string of text and a target language as input,
        and return the translated text as a string. This method serves as a
        blueprint for translation functionality in subclasses.
        :param target_language: Specifies the language into which the input
        texts should be translated.
        :param texts: A string containing the text to be translated into the
        specified target language.
        :return: The translated text in the specified target language.
        """


class FreeTranslator(Translator):
    api_url = "https://api.mymemory.translated.net/get"

    def _translate(self, text: str, target_language: str) -> str:
        """
        The `_translate` function takes a string of text and a target language
        code as input, sends a request to a translation API, and returns the
        translated text if the request is successful; otherwise, it raises a
        ValueError.
        :param target_language: Specifies the language code to which the input
        text should be translated.
        :param text: A string containing the text to be translated into the
        specified target language.
        :return: The translated text in the specified target language.
        """
        params = {"q": text, "langpair": f"en|{target_language}"}
        response = requests.get(self.api_url, params=params)
        if response.status_code == 200:
            return response.json()["responseData"]["translatedText"]
        raise ValueError


def threaded_translator(translator: Translator) -> Translator:
    """
    The `threaded_translator` function enhances a given `Translator` instance
    by creating a `ThreadedTranslator` class that allows for concurrent
    translation of multiple texts using a thread pool, improving efficiency. It
    utilizes a maximum of five worker threads to perform translations in
    parallel, returning a list of translated texts.
    :param translator: :param translator: A class that enhances a given
    Translator by enabling concurrent translation of multiple texts using a
    thread pool for improved performance.
    :return: A class that enables concurrent translation of multiple texts
    using a specified translator.
    """

    class ThreadedTranslator(type(translator)):
        def __init__(self, translator: Translator):
            """
            The `__init__` function initializes an instance of a class by accepting
            a `Translator` object and setting up a thread pool executor with a
            maximum of five worker threads for concurrent task execution.
            :param translator: An instance of the Translator class used for
            handling translation tasks within the function.
            :return: an instance of the class with a translator and a thread pool
            executor.
            """  # noqa: E501
            self.translator = translator
            self.executor = ThreadPoolExecutor(max_workers=5)

        def _translate(self, text: str, target_language: str) -> str:
            """
            The `_translate` function takes a string `text` and a `target_language`
            as inputs, and returns the translated version of the text by invoking
            the `_translate` method of the `translator` object. It serves as a
            wrapper to facilitate translation functionality within the class.
            :param target_language: Specifies the language into which the input
            text should be translated.
            :param text: A string representing the text to be translated into the
            specified target language.
            :return: The translated text in the specified target language.
            """  # noqa: E501
            return self.translator._translate(text, target_language)

        def translate(
            self, texts: Iterable[str], target_language: str
        ) -> List[str]:
            """
            The `translate` function asynchronously translates a list of input
            texts into a specified target language using a concurrent executor,
            returning a list of the translated results. It submits translation
            tasks for each text and collects the results once all tasks are
            completed.
            :param target_language: Specifies the language into which the provided
            texts will be translated.
            :param texts: An iterable collection of strings representing the texts
            to be translated into the specified target language.
            :return: A list of translated texts in the specified target language.
            """  # noqa: E501
            futures = []
            with self.executor as executor:
                for text in texts:
                    future = executor.submit(
                        self._translate, text, target_language
                    )
                    futures.append(future)
            results = [future.result() for future in futures]
            return results

    return ThreadedTranslator(translator)
