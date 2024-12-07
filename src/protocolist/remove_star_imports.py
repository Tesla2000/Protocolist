from __future__ import annotations

import collections
import typing

from protocolist.config import Config


def remove_star_imports(config: Config):
    content = config.interfaces_path.read_text()
    collection_elements = frozenset(collections.abc.__all__)
    typing_elements = frozenset(typing.__all__).difference(collection_elements)
    content = content.replace(
        "from typing import *",
        "".join(map("from typing import {}\n".format, typing_elements)),
    )
    content = content.replace(
        "from collections.abc import *",
        "".join(
            map("from collections.abc import {}\n".format, collection_elements)
        ),
    )
    config.interfaces_path.write_text(content)
