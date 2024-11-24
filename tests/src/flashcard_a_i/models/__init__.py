from __future__ import annotations

from pathlib import Path

from tests.src.flashcard_a_i import import_python
from tests.src.flashcard_a_i.models.base import Base
from tests.src.flashcard_a_i.models.connection import db

db.create_tables(
    set(
        filter(
            Base.__subclasscheck__,
            filter(
                lambda elem: isinstance(elem, type) and elem != Base,
                (
                    getattr(module, name)
                    for module in import_python(Path(__file__).parent)
                    for name in dir(module)
                ),
            ),
        )
    )
)
