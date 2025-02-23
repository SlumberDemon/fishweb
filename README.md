# Fishweb

Fishweb is a web app manager that makes running static & Python ASGI/WSGI apps effortless.

Map domains to folders on your filesystem.

- `https://example.sofa.sh` maps to `~/fishweb/example`

Turn a new folder into a website hassle-free.

## Examples

You can view the examples by cloning the repo, running the following commands in it, and visiting an example's subdomain.

```shell
uv sync --all-extras
fishweb serve --root examples
```

- <http://asgi.localhost:8888> - A simple ASGI callable example
- <http://fastapi.localhost:8888> - A FastAPI example
- <http://flask.localhost:8888> - A Flask example
- <http://static.localhost:8888> - A static website example
- <http://nested.sub.localhost:8888> - A nested subdomain example

You can also use Fishweb to serve the documentation.

```shell
cd docs
npm install && npm run docs:build
cd ..
fishweb serve --root docs/.vitepress
```

The docs will then be available at <http://dist.localhost:8888>

## Documentation

View the full docs [here](https://fishweb.sofa.sh).

## Inspirations

Projects that have shaped Fishweb with concepts, designs, and ideas.

- [smallweb](https://github.com/pomdtr/smallweb)
- [deta.space](https://github.com/deta/space-docs)
