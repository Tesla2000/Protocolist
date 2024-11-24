from __future__ import annotations

import argparse
from types import GenericAlias
from typing import Any


class CustomArgumentParser(argparse.ArgumentParser):
    def add_argument(
        self,
        *args,
        **kwargs,
    ):
        """
        The `add_argument` function modifies the behavior of adding
        command-line arguments by adjusting the `type` and `nargs` parameters
        based on the specified type, specifically handling boolean, list, and
        tuple types. It then calls the superclass's `add_argument` method to
        finalize the argument addition.
        :return: A modified argument configuration for command-line parsing.
        """
        if isinstance(kwargs.get("type"), GenericAlias):
            kwargs["type"] = kwargs.get("type").__origin__
        if isinstance(kwargs.get("type"), type):
            if issubclass(kwargs.get("type"), bool):
                kwargs["type"] = self._str2bool
            elif issubclass(kwargs.get("type"), list):
                kwargs["nargs"] = "*"
                kwargs["type"] = str
            elif issubclass(kwargs.get("type"), tuple):
                kwargs["nargs"] = "+"
                kwargs["type"] = str
        super().add_argument(
            *args,
            **kwargs,
        )

    def _str2bool(self, v: Any) -> Any:
        """
        The `_str2bool` function converts various string representations of
        boolean values into actual boolean types, returning `True` for
        affirmative strings and `False` for negative ones. If the input is not
        a recognized boolean representation, it raises an `ArgumentTypeError`.
        :param v: This parameter represents a value that can be interpreted as
        a boolean, accepting various string representations of true and false,
        or a direct boolean input.
        :return: A boolean value indicating true or false based on input.
        """
        if isinstance(v, bool):
            return v
        if v.lower() in ("yes", "true", "t", "y", "1"):
            return True
        elif v.lower() in ("no", "false", "f", "n", "0"):
            return False
        else:
            raise argparse.ArgumentTypeError(
                f"Boolean value expected got {v}."
            )
