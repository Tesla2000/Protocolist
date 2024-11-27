from __future__ import annotations

from typing import Optional

from sklearn.model_selection import train_test_split

from tests.src.flashcard_a_i.flashcard_ai.learn_criterion.AI_component.AI_loop.AI_models.ai_model import (  # noqa: E501
    AIModel,
)
from tests.src.flashcard_a_i.flashcard_ai.learn_criterion.AI_component.AI_loop.AI_tester.ai_tester import (  # noqa: E501
    AITester,
)
from tests.src.flashcard_a_i.flashcard_ai.learn_criterion.AI_component.AI_loop.AI_trainer.ai_trainer import (  # noqa: E501
    AITrainer,
)
from tests.src.flashcard_a_i.flashcard_ai.learn_criterion.AI_component.data_creator.data_creator import (  # noqa: E501
    DataCreator,
)


class Trainer:
    def __init__(
        self,
        data_creator: DataCreator,
        ai_trainer: AITrainer,
        ai_tester: Optional[AITester] = None,
        test_split: float = 0.2,
    ):
        """
        Initializes the Trainer class with instances of DataCreator and
        AITrainer, along with optional parameters for testing and data
        splitting.
        :param ai_trainer: An instance of the AITrainer class responsible for
        training the AI model using the provided data.
        :param data_creator: An instance of the DataCreator class responsible
        for generating and managing the data used for training the AI model.
        :param test_split: A float representing the proportion of data to be
        used for testing.
        :param ai_tester: An optional instance of AITester for evaluating the
        AI model.
        :return: An initialized Trainer instance.
        """
        self.ai_tester = ai_tester
        self.test_split = test_split
        self.ai_trainer = ai_trainer
        self.data_creator = data_creator
        self._x_train = None
        self._x_test = None
        self._y_train = None
        self._y_test = None
        self._x, self._y = None, None
        self._model = None

    def train(self) -> AIModel:
        """
        The `train` function generates training data using a data creator,
        processes it into feature and label arrays, and then trains an AI model
        using the processed data. It returns the trained AITrainer instance.
        :return: An AITrainer instance trained on the provided data.
        """
        if self._is_data_generated():
            return self.ai_trainer.train(self._x_train, self._y_train)
        self._generate_data()
        self._model = self.ai_trainer.train(self._x_train, self._y_train)
        return self._model

    def test(self):
        """
        The `test` function evaluates the AI model using test data, generating
        the data if it hasn't been created yet.
        :return: Test results from the AI model.
        """
        if self._is_data_generated():
            return self.ai_tester.test(self._model, self._x_test, self._y_test)
        self.train()
        return self.ai_tester.test(self._model, self._x_test, self._y_test)

    def _generate_data(self):
        """
        Generates training and testing data by creating combined datasets and
        splitting them based on the specified test size.
        :return: None
        """
        self._x, self._y = self.data_creator.create_data_combined()
        if self.test_split == 0:
            self._x_train, self._y_train = self._x, self._y
            self._x_test, self._y_test = self._x, self._y
            return
        self._x_train, self._x_test, self._y_train, self._y_test = (
            train_test_split(
                self._x, self._y, test_size=self.test_split, stratify=self._y
            )
        )

    def _is_data_generated(self):
        """
        Checks if the training and testing data have been generated by
        verifying that none of the data sets are None.
        :return: Boolean indicating data generation status.
        """
        return not any(
            set is None
            for set in (
                self._x_train,
                self._x_test,
                self._y_train,
                self._y_test,
            )
        )
