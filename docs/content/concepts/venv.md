# Virtual environment

In order to run a python app with a framework or additional libraries you need a virtual environment with them installed.
The default virtual environment folder fishweb will check is `.venv` this can be changed in the [config](/content/reference/config#venv-path).

:::warning Notice
The version of python in your virtual environment must be the same as the version which you installed fishweb with.
:::

## Create

```sh
uv venv [path]
```

To specifiy a python version use the `--python` flag. The default path is `.venv`.

```sh
python -m venv .venv
```
