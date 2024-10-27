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
