from __future__ import annotations

from uuid import uuid4

from peewee import CharField
from peewee import Model

from .connection import db


class Base(Model):
    uuid = CharField()

    def __init__(self, *args, **kwargs):
        """
        The `__init__` function initializes an object by ensuring that a unique
        identifier (`uuid`) is set in the `kwargs` dictionary, defaulting to a
        newly generated UUID if none is provided. It then calls the parent
        class's `__init__` method with the given arguments and updated keyword
        arguments.
        :return: A unique identifier (UUID) for the instance.
        """
        kwargs["uuid"] = kwargs.get("uuid", str(uuid4()))
        super().__init__(*args, **kwargs)

    class Meta:
        database = db
