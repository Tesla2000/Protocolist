from __future__ import annotations

import os

from peewee import SqliteDatabase

db = SqliteDatabase(os.getenv("SQLITE_PATH"))
db.connect()
