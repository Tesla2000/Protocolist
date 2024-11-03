from typing import Iterator

from mypy.memprofile import defaultdict


class ProtocolDict(defaultdict):
    def get_protocols(self) -> Iterator[str]:
        for key, value in tuple(self.items()):
            for i in range(value):
                i = str(i + 1)
                yield key + i