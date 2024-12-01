## Running

You can run script with docker, python or from cmd

### Python
```shell
python main.py --config_file src/protocolist/config_sample.toml
```

### Cmd
```shell
poetry install
poetry run protocolist
```

### Docker

```shell
docker build -t Protocolist .
docker run -it Protocolist /bin/sh
python main.py
```
