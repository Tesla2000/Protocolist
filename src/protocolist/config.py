from __future__ import annotations

import os
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any
from typing import Optional
from typing import Type

import toml
from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic import Field
from pydantic_core import PydanticUndefined

from .custom_argument_parser import CustomArgumentParser
from .presentation_option.presentation_option import PresentationOption
from .protocol_markers.mark_options import MarkOption
from .utils.filepath2import_path import filepath2import_path

load_dotenv()


class Config(BaseModel):
    _root: Path = Path(__file__).parent
    project_root: Path = Path(os.getcwd())
    pos_args: list[str] = Field(default_factory=list)
    mypy_folder: Path = _root / ".temp"
    config_file: Optional[Path] = None
    interfaces_path: Path
    interfaces_path_origin: Path
    allow_any: bool = False
    mark_option: MarkOption = MarkOption.ALL
    protocol_presentation: PresentationOption = (
        PresentationOption.COMBINED_PROTOCOLS
    )
    external_libraries: Optional[Iterable[str]] = tuple()
    excluded_libraries: Iterable[str] = tuple()
    tab_length: int = 4
    keep_hints: bool = True
    max_hint_length: int = sys.maxsize

    def __init__(self, /, **data: Any):
        data["interfaces_path"] = Path(
            data.get(
                "interfaces_path",
                Path(os.getcwd())
                / data.get("interfaces_path_origin", "interfaces")
                / "interfaces.py",
            )
        )
        data["interfaces_path_origin"] = data["interfaces_path"].parent
        data["interfaces_path_origin"].mkdir(exist_ok=True)
        if not data["interfaces_path"].exists():
            data["interfaces_path"].write_text("")
        super().__init__(**data)
        self.excluded_libraries = frozenset(self.excluded_libraries).union(
            {"networkx.utils.configs"}
        )

    @property
    def interface_import_path(self) -> str:
        return filepath2import_path(
            self.interfaces_path, project_root=self.project_root
        )


def parse_arguments(config_class: Type[Config]):
    parser = CustomArgumentParser(
        description="Configure the application settings."
    )

    for name, value in config_class.model_fields.items():
        if name.startswith("_"):
            continue
        annotation = value.annotation
        if len(getattr(value.annotation, "__args__", [])) > 1:
            annotation = next(filter(None, value.annotation.__args__))
        parser.add_argument(
            f"--{name}" if name != "pos_args" else name,
            type=annotation,
            default=value.default,
            help=f"Default: {value}",
        )

    return parser.parse_args()


def create_config_with_args(config_class: Type[Config], args) -> Config:
    arg_dict = {
        name: getattr(args, name)
        for name in config_class.model_fields
        if hasattr(args, name) and getattr(args, name) != PydanticUndefined
    }
    if arg_dict.get("config_file") and Path(arg_dict["config_file"]).exists():
        config = config_class(
            **{
                **arg_dict,
                **toml.load(arg_dict.get("config_file")),
            }
        )
    else:
        config = config_class(**arg_dict)
    for variable in config.model_fields:
        value = getattr(config, variable)
        if (
            isinstance(value, Path)
            and value.suffix == ""
            and not value.exists()
        ):
            value.mkdir(parents=True)
    return config
