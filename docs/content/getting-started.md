# Getting started

:::warning Notice
Fishweb is still in the early stages of development and therefore may be subject to receiving breaking changes frequently.
Additionally, Fishweb is not responsible for securing your server or apps. If you decide to use Fishweb in production, make sure to implement proper security.
:::

## Why fishweb?

## Installation

### UV

UV is the **recommended** way to install Fishweb. You can install Fishweb as a full CLI, or if you want to run Fishweb with your own ASGI server, install Simple.

::: code-group

```sh [Full CLI]
uv tool install fishweb[serve,reload]
```

```sh [Simple]
uv tool install fishweb
```

```sh [Dev]
git clone https://github.com/slumberdemon/fishweb
cd fishweb
uv tool install .
```

:::

### PIP

::: code-group

```sh [Full CLI]
pip install -U fishweb[serve,reload]
```

```sh [Simple]
pip install fishweb
```

```sh [Dev]
git clone https://github.com/slumberdemon/fishweb
cd fishweb
pip install .
```
