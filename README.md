## Running

You can run script with docker or python

### Python
```shell
python main.py --config_file src/interfacer/config_sample.toml
```

### Docker

```shell
docker build -t Interfacer .
docker run -it Interfacer /bin/sh
python main.py
```
