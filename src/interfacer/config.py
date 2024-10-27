from __future__ import annotations

from pathlib import Path
from typing import Type, Optional

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic import Field

from .custom_argument_parser import CustomArgumentParser

load_dotenv()


class Config(BaseModel):
    _root: Path = Path(__file__).parent
    pos_args: list[str] = Field(default_factory=list)
    config_file: Optional[Path] = None


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
        name: getattr(args, name) for name in config_class.model_fields if hasattr(args, name)
    }
    if (
        arg_dict.get("config_file")
        and Path(arg_dict["config_file"]).exists()
    ):
        config = config_class(
            **{
                **arg_dict, **toml.load(arg_dict.get("config_file")),
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