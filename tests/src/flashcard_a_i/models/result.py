from __future__ import annotations

from peewee import BooleanField
from peewee import CharField
from peewee import ForeignKeyField
from peewee import TimestampField

from .base import Base
from .user import User


class Result(Base):
    date = TimestampField()
    is_correct = BooleanField()
    word = CharField()
    translation = CharField()
    user = ForeignKeyField(User, backref="results")
