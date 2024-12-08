# Protocolist

Protocolist is a python script that adds missing type hints and creates matching protocols.

## How it works
Protocolist uses:
 - mypy to get information about missing type hints,
 - libcst to extract and modify relevant code.

Protocolist doesn't used LLMs making generation process confidential, deterministic, and possible offline. 


## Setup
```shell
git clone https://github.com/Tesla2000/Protocolist.git
cd Protocolist
```
```shell
poetry install
```
OR (Linux / Mac)
```shell
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
OR (Windows)
```shell
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

## Running

You can run script with docker, python or from cmd

### Python
```shell
python main.py file1.py file2.py --config_file src/protocolist/config_sample.toml
```

### Cmd
```shell
poetry run protocolist file1.py file2.py
```
```shell
protocolist file1.py file2.py
```

### Docker

```shell
docker build -t Protocolist .
docker run -it Protocolist /bin/sh
python main.py
```

## Known issues
 - Slow type hint generation due to dependency on mypy,
 - ORM issue in previously defined protocols,
 - Re-running scripts causing unintended changes,
 - Other https://github.com/Tesla2000/Protocolist/issues.
