# Fishweb

Fishweb is a simple cli that makes it easy to run Python ASAGI applications effortlessly. It may be thought of as the Python equivalent of [smallweb](https://github.com/pomdtr/smallweb).

Map domains to folders in your filesystem.

- `https://example.sofa.sh` maps to `~/fishweb/example`

Turn a new folder into a website without the need to start a development server or even setup a virtual environment.

## Documentation

### Prerequisite

- [UV](https://docs.astral.sh/uv/getting-started/installation/)

### Installation

```shell
git clone https://github.com/slumberdemon/fishweb
cd fishweb
```

#### UV (recommended)

```shell
uv tool install .
```

Now you should be able to run `fishweb` and see the help menu!

View the full docs [here]()

## Inspirations

Projects that have shaped fishweb with it's concepts, design and ideas.

- [smallweb](https://github.com/pomdtr/smallweb)
- [deta.space](https://github.com/deta/space-docs)
