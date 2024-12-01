from __future__ import annotations

from collections.abc import Iterator

from mypy.memprofile import defaultdict

from .to_camelcase import to_camelcase


class ProtocolDict(defaultdict):
    def get_protocols(self) -> Iterator[str]:
        for key, value in tuple(self.items()):
            for i in range(value):
                i = str(i + 1)
                yield key + i

    def __getitem__(self, item):
        return super().__getitem__(to_camelcase(item))

    def __setitem__(self, key, value):
        return super().__setitem__(to_camelcase(key), value)
