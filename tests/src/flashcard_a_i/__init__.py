from __future__ import annotations

from importlib import import_module
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def import_python(root: Path):
    """
    The `import_python` function recursively imports Python modules from a
    specified directory, excluding `__init__.py`, `pycache`, and files within
    it, while yielding the imported modules with their relative paths. It
    constructs the module names based on the directory structure, allowing for
    dynamic module loading.
    :param root: A `Path` object representing the directory from which Python
    modules will be imported recursively.
    :return: A generator yielding imported modules from a specified directory
    path.
    """
    for module_path in root.iterdir():
        if module_path.name in ("__init__.py", "pycache") or (
            module_path.suffix != ".py" and not module_path.is_dir()
        ):
            continue
        if module_path.is_file():
            relative_path = module_path.relative_to(Path(__file__).parent)
            subfolders = "".join(map(".{}".format, relative_path.parts[:-1]))
            str_path = module_path.with_suffix("").name
            yield import_module("." + str_path, __name__ + subfolders)
            continue
        yield from import_python(module_path)


__all__ = list(import_python(Path(__file__).parent))
