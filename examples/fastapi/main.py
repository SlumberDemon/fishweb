import pyjokes
from fastapi import FastAPI
from fastapi.exceptions import HTTPException

app = FastAPI()


@app.get("/")
async def read_root() -> dict[str, str]:
    return {"message": "Hello from FastAPI!"}


@app.get("/joke")
async def read_joke() -> dict[str, str]:
    return {"joke": pyjokes.get_joke()}


@app.get("/error")
async def error() -> None:
    raise ZeroDivisionError


@app.get("/http-exception")
async def http_exception() -> None:
    raise HTTPException(status_code=418, detail="I'm a Teapot")
