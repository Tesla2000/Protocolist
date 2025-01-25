from __future__ import annotations

from collections.abc import Collection
from collections.abc import Iterable
from collections.abc import Sequence
from pathlib import Path
from typing import NamedTuple

from protocolist.convert_relative_to_absolute import convert_relative_path
from protocolist.transform.class_extractor import GlobalClassExtractor


class _ImportLink(NamedTuple):
    from_import: Path
    to_import: Path


def link_files_by_imports(
    paths: Sequence[Path], global_class_extractor: GlobalClassExtractor
) -> Sequence[_ImportLink]:
    return tuple(
        _ImportLink(import_path.absolute(), path.absolute())
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
        if import_path.exists()
        and (import_path in paths or import_path.absolute() in paths)
    )


def sort_paths_by_import_links(
    paths: Iterable[Path], import_links: Collection[_ImportLink]
) -> list[Path]:
    paths_in_order = []
    paths = list(paths)
    while paths:
        for path in tuple(map(Path.absolute, paths)):
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
