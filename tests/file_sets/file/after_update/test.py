from __future__ import annotations

from tests.file_sets.file.before_update.protocols import IOClass


def foo(file: IOClass) -> None:
    file.read(2)
    file.tell()
