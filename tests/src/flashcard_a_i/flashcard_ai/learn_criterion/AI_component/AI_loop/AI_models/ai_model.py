from __future__ import annotations

from typing import Protocol
from typing import runtime_checkable

from numpy import ndarray


@runtime_checkable
class AIModel(Protocol):
    def predict_proba(self, X: ndarray[ndarray]) -> ndarray[float]:
        """
        The `predict_proba` function is an abstract method intended to be
        implemented in subclasses, which should return the predicted
        probabilities for the given input data `X`. Currently, it raises a
        `NotImplementedError`, indicating that the function must be defined in
        a derived class.
        :param X: An array of input features used to predict the probability of
        a certain outcome.
        :return: The predicted probabilities for each class in the input data.
        """
        raise NotImplementedError

    def predict(self, X: ndarray[ndarray]) -> ndarray[int]:
        """
        This method is intended to be implemented in subclasses to return
        predicted class labels for the input data `X`. It currently raises a
        `NotImplementedError`, indicating that the function must be defined in
        a derived class.
        :param X: An array of input features used to predict class labels.
        :return: Predicted class labels for the input data.
        """
        raise NotImplementedError
