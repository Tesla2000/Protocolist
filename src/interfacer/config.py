from __future__ import annotations

import os
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

load_dotenv()


class Config(BaseModel):
    _root: Path = Path(__file__).parent
    pos_args: list[str] = Field(default_factory=list)
    mypy_folder: Path = _root / ".temp"
    config_file: Optional[Path] = None
    interfaces_path: Path
    interfaces_path_origin: Path
    allow_any: bool = False

    def __init__(self, /, **data: Any):
        data["interfaces_path"] = Path(
            data.get(
                "interfaces_path", os.getcwd() + "/interfaces/interfaces.py"
            )
        )
        data["interfaces_path_origin"] = data["interfaces_path"].parent
        super().__init__(**data)


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
