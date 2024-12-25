from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import NamedTuple

from protocolist.convert_relative_to_absolute import convert_relative_path
from protocolist.transform.class_extractor import GlobalClassExtractor


class _ImportLink(NamedTuple):
    from_import: Path
    to_import: Path


def sort_files_by_import_order(
    paths: Sequence[Path], global_class_extractor: GlobalClassExtractor
) -> list[Path]:
    import_links = tuple(
        _ImportLink(import_path, path)
        for path, extractor in zip(
            paths, map(global_class_extractor.get, paths)
        )
        for import_path in map(
            Path,
            map(
                lambda import_path: convert_relative_path(
                    path, import_path
                ).replace(".", "/")
                + ".py",
                extractor.imports.keys(),
            ),
        )
        if import_path.exists() and import_path in paths
    )
    paths_in_order = []
    paths = list(paths)
    while paths:
        for path in tuple(paths):
            if path not in tuple(link.to_import for link in import_links):
                paths_in_order.append(path)
                import_links = tuple(
                    filter(lambda link: link.from_import != path, import_links)
                )
                paths.remove(path)
                break
        else:
            raise ValueError
    return paths_in_order
