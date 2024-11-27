from __future__ import annotations

from pathlib import Path

from bs4 import BeautifulSoup

from tests.src.flashcard_a_i.word_extraction.word_extracotors.extracotor import (  # noqa: E501
    WordExtractor,
)


class HTMLWordExtractor(WordExtractor):
    @staticmethod
    def extract(file_path: str) -> set[str]:
        """
        The `extract` function reads the content of a specified file, parses it
        as HTML using BeautifulSoup, and returns a set of words extracted from
        the text. If the file does not exist, it raises a `FileNotFoundError`.
        :param file_path: A string representing the path to the file that will
        be read and processed to extract text.
        :return: A set of unique words extracted from the text content of the
        specified file.
        """
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"No such file: '{file_path}'")

        content = path.read_text(encoding="utf-8")
        soup = BeautifulSoup(content, "html.parser")
        text = soup.get_text()
        return text.split()


if __name__ == "__main__":
    extractor = HTMLWordExtractor()
    words = extractor.extract("html_files/superconductors.html")
    print(words)
