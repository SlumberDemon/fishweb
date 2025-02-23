# Getting Started

> [!WARNING]
> Fishweb is still in the early stages of development and therefore may be subject to receiving breaking changes frequently.
> Additionally, Fishweb is not responsible for securing your server or apps. If you decide to use Fishweb in production, make sure to implement proper security.

## Why Fishweb?

Fishweb is a simple app web manager made to be small and easy to use.
If you like iterating fast or have lots of ideas and projects, fishweb's folder-based routing and live reloading makes it hassle-free.
Fishweb is personal in the sense that you don't have to depend on cloud providers to host your apps.

## Installation

### uv

uv is the **recommended** way to install Fishweb.
You can install Fishweb with [uvicorn](https://www.uvicorn.org/) as a built-in server, or if you want to run your own ASGI server you can install it without extra dependencies.

::: code-group

```sh [Server]
uv tool install fishweb[serve]
```

```sh [Simple]
uv tool install fishweb
```

```sh [From source]
git clone https://github.com/slumberdemon/fishweb
cd fishweb
uv tool install .
```

:::

### pip

::: code-group

```sh [Server]
pip install fishweb[serve]
```

```sh [Simple]
pip install fishweb
```

```sh [From source]
git clone https://github.com/slumberdemon/fishweb
cd fishweb
pip install .
```

### Extras

- `serve`: Installs [uvicorn](https://www.uvicorn.org/) as a built-in ASGI server to enable the `fishweb serve` comand
- `reload`: Installs [watchdog](https://python-watchdog.readthedocs.io/en/stable/index.html) to enable live reloading of apps
- `wsgi`: Installs [asgiref](https://github.com/django/asgiref) for WSGI compatibility

You can install all extras by using `fishweb[serve,reload,wsgi]` as the package name.
