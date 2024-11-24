from __future__ import annotations

import requests
from bs4 import BeautifulSoup

from tests.src.flashcard_a_i.word_extraction.word_extracotors.extracotor import (  # noqa: E501
    WordExtractor,
)


class WebsiteWordExtractor(WordExtractor):

    @staticmethod
    def extract(url):
        """
        The `extract` function retrieves the HTML content from a given URL,
        parses it using BeautifulSoup, and returns a list of words extracted
        from the text. It raises an error if the HTTP request fails.
        :param url: A string representing the web address from which to
        retrieve and extract text content.
        :return: a list of words extracted from the webpage text
        """
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text()
        return text.split()
