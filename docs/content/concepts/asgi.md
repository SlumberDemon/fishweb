# ASGI Apps

[ASGI](https://asgi.readthedocs.io/en/latest/index.html) apps are written in Python and provide an ASGI callable called `app` in a `main.py` file.
You can also [configure the entrypoint](/content/reference/config#entry) for different project structures.

If the [live reload](/content/concepts/reload) feature is enabled, changes to the app's folder on disk will be reflected in real-time.
Otherwise, changes will only be visible after restarting Fishweb.

## Basic

In Fishweb, it's possible to write simple ASGI apps without the need for a framework, virtual environment, or even a Fishweb config file.

::: code-group

```py [main.py]
async def app(scope, receive, send):
    if scope["type"] != "http":
        return
    await send(
        {
            "type": "http.response.start",
            "status": 200,
            "headers": [[b"content-type", b"text/plain"]],
        },
    )
    await send(
        {
            "type": "http.response.body",
            "body": b"Hello from a pure ASGI app!",
        },
    )
```

:::

## Framework

However you can also use any [ASGI framework](https://www.uvicorn.org/#asgi-frameworks) with Fishweb.
Here is an example using [FastAPI](https://fastapi.tiangolo.com/).

> [!IMPORTANT]
> When using a framework make sure you have it installed inside a [virtual environment](/content/concepts/venv).

::: code-group

```py [main.py]
from typing import Union
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
```

```txt [requirements.txt]
fastapi
```

:::
