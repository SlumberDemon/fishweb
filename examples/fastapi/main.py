import pyjokes
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def read_root() -> dict[str, str]:
    return {"message": "Hello from FastAPI!"}


@app.get("/joke")
async def read_joke() -> dict[str, str]:
    return {"joke": pyjokes.get_joke()}
