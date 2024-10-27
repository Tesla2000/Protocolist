from __future__ import annotations

from src.interfacer.config import parse_arguments, Config, \
    create_config_with_args


def main():
    """
    The `main` function parses command-line arguments using a specified
    configuration, creates a configuration object based on those arguments, and
    then prints the resulting configuration.
    :return: A configuration object created from parsed command-line arguments.
    """
    args = parse_arguments(Config)
    config = create_config_with_args(Config, args)
    print(config)


if __name__ == "__main__":
    exit(main())
