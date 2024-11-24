from __future__ import annotations

from .normalize_words import SequenceNormalizerStrategy
from .printers.printer import Printer
from .train_filter.train_filter import TrainFilter
from .translator.translator import Translator
from .word_extracotors.extracotor import WordExtractor
from .word_scorer import WikiWordsProcessor


class WordExtraction:
    def __init__(
        self,
        word_extractor: WordExtractor,
        word_normalizer: SequenceNormalizerStrategy,
        word_scorer: WikiWordsProcessor,
        train_filter: TrainFilter,
        translator: Translator,
        printer: Printer,
    ):
        """
        The `__init__` function initializes an object with various components
        for processing words, including a word extractor, normalizer, scorer,
        filter, translator, and printer, allowing for customizable text
        handling and analysis. Each parameter is designed to facilitate
        specific tasks in the overall word processing workflow.
        :param printer: A Printer is responsible for outputting or displaying
        information in a specified format during the execution of the program.
        :param word_normalizer: A strategy for normalizing words, which may
        involve processes such as stemming, lemmatization, or standardization
        to ensure consistency in word representation.
        :param train_filter: A mechanism for filtering training data based on
        specified criteria to enhance the quality and relevance of the training
        process.
        :param word_scorer: An instance of the WikiWordsProcessor class
        responsible for scoring words based on their relevance or importance in
        the context of the application.
        :param word_extractor: An instance of the WordExtractor class
        responsible for extracting words from a given input source.
        :param translator: :param translator: An instance of the Translator
        class responsible for converting words or phrases from one language to
        another.
        :return: An instance of a class initialized with various processing
        components for text analysis.
        """
        self.printer = printer
        self.translator = translator
        self.train_filter = train_filter
        self.word_scorer = word_scorer
        self.word_normalizer = word_normalizer
        self.word_extractor = word_extractor
        self.word_extractor = word_extractor

    def run(self, *args, **kwargs) -> dict[str, str]:
        """
        The `run` function processes input arguments to extract, normalize, and
        filter words, then translates the filtered words into Polish and prints
        the resulting dictionary of word translations. It returns this
        dictionary, mapping each filtered word to its corresponding
        translation.
        :return: A dictionary mapping filtered words to their Polish
        translations.
        """
        words = self.word_extractor.extract(*args, **kwargs)
        words = self.word_normalizer.normalize(words)
        words = self.word_scorer.sort_words_by_position_desc(words)
        filtered_words = self.train_filter.filter_words(words)
        result = dict(
            zip(
                filtered_words, self.translator.translate(filtered_words, "pl")
            )
        )
        self.printer.print(result)
        return result
