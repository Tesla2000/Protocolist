from __future__ import annotations

from tests.src.flashcard_a_i.models.result import Result
from tests.src.flashcard_a_i.models.user import User


class UserService:
    @staticmethod
    def get_results(user: User):
        """
        The `get_results` static method retrieves all `Result` records
        associated with a specified `User`. It returns a query result set
        filtered by the provided user instance.
        :param user: An instance of the User class representing the user for
        whom results are being retrieved.
        :return: A queryset of Result objects associated with the specified
        user.
        """
        return Result.select().where(Result.user == user)
