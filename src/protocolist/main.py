from __future__ import annotations

import os
import re
from itertools import compress
from itertools import filterfalse
from multiprocessing import Manager
from multiprocessing import Pool
from operator import itemgetter
from pathlib import Path

from .add_inheritance import add_inheritance
from .config import Config
from .config import create_config_with_args
from .config import parse_arguments
from .presentation_option.protocol_saver_factory import create_protocol_saver
from .protocol_dict import ProtocolDict
from .protocol_markers.types_marker_factory import create_type_marker
from .remove_star_imports import remove_star_imports
from .sort_paths_by_import_links import link_files_by_imports
from .sort_paths_by_import_links import sort_paths_by_import_links
from .transaction import transation
from .transform.class_extractor import ClassExtractor
from .transform.class_extractor import GlobalClassExtractor
from .transform.create_protocols import create_protocols
from .utils.lock import lock


def main() -> int:
    args = parse_arguments(Config)
    config = create_config_with_args(Config, args)
    with transation(config.pos_args, config):
        return protocol(config)


def protocol(config: Config) -> int:
    paths = tuple(
        map(
            Path.absolute,
            filter(
                lambda path: path.suffix == ".py", map(Path, config.pos_args)
            ),
        )
    )
    global_class_extractor = GlobalClassExtractor(config)
    import_links = link_files_by_imports(paths, global_class_extractor)
    paths = sort_paths_by_import_links(paths, import_links)
    classes = ClassExtractor(
        config, create_type_marker(config)
    ).extract_classes(config.interfaces_path.read_text())
    interfaces = dict(
        sorted(
            (
                (item[0][0], int(item[0][1]))
                for item in map(
                    lambda name: re.findall(r"(\D+)(\d+)", name),
                    classes.keys(),
                )
                if item
            ),
            key=itemgetter(1),
        )
    )
    if config.n_workers > 1:
        is_file_modified = {}

        def task_done_callback(result: tuple[int, Path]):
            nonlocal import_links
            is_modified, path = result
            is_file_modified[path] = is_modified

            with lock:
                import_links = tuple(
                    filter(lambda link: link.from_import != path, import_links)
                )
                new_executing = list(
                    filterfalse(
                        executing.__contains__,
                        filterfalse(
                            tuple(
                                link.to_import for link in import_links
                            ).__contains__,
                            paths,
                        ),
                    )
                )
                executing.extend(new_executing)
            with Pool(processes=config.n_workers) as pool:
                for path in new_executing:
                    pool.apply_async(
                        create_protocols,
                        kwds=dict(
                            filepath=path,
                            config=config,
                            protocols=protocols,
                            class_extractor=global_class_extractor,
                        ),
                        callback=task_done_callback,
                        error_callback=error_callback,
                    )
                pool.close()
                pool.join()

        with Pool(processes=config.n_workers) as pool, Manager() as manager:
            protocols = manager.dict()
            protocols.update(interfaces)
            executing = list(
                filterfalse(
                    tuple(
                        link.to_import for link in import_links
                    ).__contains__,
                    paths,
                )
            )
            for path in executing:
                pool.apply_async(
                    create_protocols,
                    kwds=dict(
                        filepath=path,
                        config=config,
                        protocols=protocols,
                        class_extractor=global_class_extractor,
                    ),
                    callback=task_done_callback,
                    error_callback=error_callback,
                )
            pool.close()
            pool.join()
        is_file_modified = tuple(map(is_file_modified.__getitem__, paths))
    else:
        protocols = ProtocolDict(int, **interfaces)
        is_file_modified = tuple(
            create_protocols(
                filepath,
                config=config,
                protocols=protocols,
                class_extractor=global_class_extractor,
            )[0]
            for filepath in paths
        )
    create_protocol_saver(config).modify_protocols()
    is_file_modified = tuple(
        add_inheritance(
            filepath, config=config, class_extractor=global_class_extractor
        )
        or modified
        for filepath, modified in zip(paths, is_file_modified)
    )
    remove_star_imports(config)
    fail = any(is_file_modified)
    str_path = " ".join(
        f'"{path}"' for path in compress(paths, is_file_modified)
    )
    fail |= os.system(
        f"autoflake --in-place --remove-all-unused-imports "
        f"{str_path} {config.interfaces_path.absolute()}"
    )
    fail |= os.system(
        f"reorder-python-imports "
        f"{str_path} {config.interfaces_path.absolute()} --py39-plus"
    )
    return fail


def error_callback(e: Exception):
    raise e
