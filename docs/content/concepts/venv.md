# Virtual Environments

To run a Python app with a framework or additional libraries you need a virtual environment with those dependencies installed.

The default virtual environment path Fishweb will check is `.venv`, relative to your app's directory.
This can be changed in the [config](/content/reference/config#venv-path) file.

> [!IMPORTANT]
> The version of Python used in the virtual environment **must match** the version you are using to run Fishweb.

## How it works

When loading your app, Fishweb will temporarily add the virtual environment to the Python `sys.path` list, so that your app can access it during start-up.

## Creating the Virtual Environment

1. First make sure you are inside your projects root directory.
2. Then setup the `.venv` directory.

::: code-group

```sh [uv]
uv venv
```

```sh [pip]
python -m venv .venv
```

:::

3. Activate the virtual environment

```sh
source  .venv/bin/activate
```

4. Now you can install additional libaries.

Learn more about virtual environments with uv [here](https://docs.astral.sh/uv/pip/environments/#creating-a-virtual-environment) and for standard python [here](https://docs.python.org/3/library/venv.html)
