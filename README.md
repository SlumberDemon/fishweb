# Fishweb

## App structure

You can quickly create a new app with `fishweb new [name]` or create a folder in `$HOME/fishweb` which maps to `<folder-name>.localhost:8888`.

As fishweb uses uvicorn any [ASGI framework](https://www.uvicorn.org/#asgi-frameworks) is supported. Apps must have a `main.py` file and the instance must be named `app`.
They also need a `requirements.txt` file to install libraries. Environment variables should be provided in a `.env` file.

## Cloudflare

Guide soon

## Prerequisite

- [Go](https://go.dev/)
- [UV standalone](https://docs.astral.sh/uv/getting-started/installation/)
- [Uvicorn](https://pypi.org/project/uvicorn/) (optional)

Uvicorn **must** either be installed globally or added to an apps `requirements.txt`.

## Source install

> macOS and linux

```shell
# Clone and change into directory
git clone https://github.com/slumberdemon/fishweb
cd fishweb

# Get executable binary
go build

# Move to correct location
sudo cp fishweb /usr/local/bin
```


## Issues
- [ ] Find a way to stop leaving <defunct> processes
- [ ] Clean up error messages
