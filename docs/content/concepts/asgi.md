# ASGI App

ASGI apps are written in python and need a `main.py` (or other if you [configure entry](/content/reference/config#entry)).
If `reload` isn't enabled they won't update until fishweb is restarted.

## Basic

In Fishweb, it's possible to write simple ASGI apps without the need for a framework, virtual environment, or even a Fishweb config file.

::: code-group

```py [main.py]
async def app(scope, receive, send):
    assert scope["type"] == "http"
    await send(
        {
            "type": "http.response.start",
            "status": 200,
            "headers": [[b"content-type", b"text/plain"]],
        },
    )
    await send({"type": "http.response.body", "body": b"Hello from a pure ASGI app!"})
```

:::


## Framework

However you can also use any [ASGI framework](https://www.uvicorn.org/#asgi-frameworks) in fishweb.
Here is an example with [fastapi](https://pypi.org/project/fastapi/).
When using a framework make sure you have it installed inside a [virtual environment](/content/concepts/venv).

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
