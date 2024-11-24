from __future__ import annotations

from pathlib import Path
from typing import Type

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic import Field

from .custom_argument_parser import CustomArgumentParser

load_dotenv()


class Config(BaseModel):
    _root: Path = Path(__file__).parent
    words: Path = _root.parent.parent.joinpath("words") / "words_tomasz.json"
    pos_args: list[str] = Field(default_factory=list)
    model_path: Path = Path("PredictionModel.joblib")


def parse_arguments(config_class: Type[Config]):
    """
    The `parse_arguments` function creates a command-line argument parser based
    on the fields of a given configuration class, allowing users to set
    application settings via command-line options. It automatically generates
    arguments for each field, excluding private ones, and provides default
    values and help descriptions.
    :param config_class: A class that defines the configuration model,
    including its fields and their types, used to generate command-line
    arguments for application settings.
    :return: Parsed command-line arguments for application configuration.
    """
    parser = CustomArgumentParser(
        description="Configure the application settings."
    )

    for name, value in config_class.model_fields.items():
        if name.startswith("_"):
            continue
        parser.add_argument(
            f"--{name}" if name != "pos_args" else name,
            type=value.annotation,
            default=value.default,
            help=f"Default: {value}",
        )

    return parser.parse_args()


def create_config_with_args(config_class: Type[Config], args) -> Config:
    """
    The `create_config_with_args` function initializes a configuration object
    of a specified class using attributes from the provided `args`, and ensures
    that any directory paths in the configuration that do not exist are
    created. It returns the configured object after processing the necessary
    fields.
    :param args: :param args: An object containing attributes that correspond
    to the fields of the specified configuration class, used to initialize an
    instance of that class.
    :param config_class: A class type that defines the structure and fields of
    the configuration to be created.
    :return: A configured instance of the specified class, with directories
    created as needed.
    """
    config = config_class(
        **{name: getattr(args, name) for name in config_class.model_fields}
    )
    for variable in config.model_fields:
        value = getattr(config, variable)
        if (
            isinstance(value, Path)
            and value.suffix == ""
            and not value.exists()
        ):
            value.mkdir(parents=True)
    return config
