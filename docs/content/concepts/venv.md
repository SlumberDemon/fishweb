# Python Virtual Environments

To run a Python app with a framework or additional libraries you need a virtual environment with those dependencies installed.

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

## Running using a Virtual Environment

Python virtual environments include a Python bin/executable file that Fishweb needs the entire path in order to use the virtual environment's libraries. After activating, you can use 'which' to find the correct path or navigate around your virtual environment folder. This is made easier by 'uv', as it will automatically use the appropriate virtual environment.

::: code-group

```yaml [uv]
run: uv run uvicorn main:app --port $PORT
```

```yaml [python]
run: .venv/bin/python3 -m uvicorn main:app --port $PORT
```

:::
