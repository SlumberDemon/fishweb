import asyncio
import time
from pathlib import Path
from typing import Dict

import aiohttp
import typer
import uvicorn
from loguru import logger
from platformdirs import user_cache_dir
from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import PlainTextResponse, Response
from starlette.routing import Route
from typing_extensions import Annotated

from fishweb.worker import Worker

app = typer.Typer()
state = {"http_address": "localhost:8888"}


class Root(HTTPEndpoint):
    async def get(self, request):
        return PlainTextResponse("Fishweb is running")


class SubdomainMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

        self.workers: Dict[str, Worker] = {}

    async def idle_timer(self, subdomain: str, worker: Worker) -> None:
        if worker.idle and worker.active_requests == 0:
            await asyncio.sleep(10 - (time.time() - worker.idle))
            if subdomain in self.workers:
                worker.stop()
                del self.workers[subdomain]

    def get_worker(self, subdomain: str) -> Worker:
        wk = self.workers.get(subdomain)

        if wk and wk.running and wk.get_app_mtime(subdomain) < wk.started_at:
            return wk

        wk = Worker()
        self.workers[subdomain] = wk
        return wk

    async def dispatch(self, request, call_next) -> Response:
        self.address = request.headers.get("host")
        self.host = self.address.split(":")[0]
        self.subdomain = (
            "www"
            if self.address == state["http_address"]
            else self.address.split(".")[0]
        )

        app_dir = Path.home().joinpath("fishweb", self.subdomain)

        if not app_dir.exists():
            logger.warning(f"{self.subdomain} not found")
            return PlainTextResponse(f"{self.subdomain} not found", 404)

        log_path = Path(user_cache_dir("fishweb")).joinpath("domains", self.subdomain)
        logger.add(
            f"{log_path}/logs.log",
            rotation="100 MB",
            retention="28 days",
        )  # compression="zip"

        wk = self.get_worker(self.subdomain)
        wk.active_requests += 1

        try:
            port = wk.start(app_dir)
            if not port:
                wk.active_requests -= 1
                return PlainTextResponse("internal server error", 500)

            body = await request.body()
            headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}
            url = f"http://localhost:{port}{request.url.path}"
            if request.query_params:
                url += f"?{request.query_params}"

            async with aiohttp.ClientSession() as session:
                response = await session.request(
                    method=request.method,
                    url=url,
                    headers=headers,
                    data=body,
                    allow_redirects=False,  # needed?
                )

                response_headers = {
                    k: v
                    for k, v in response.headers.items()
                    if k.lower() not in ("server", "transfer-encoding")
                }

                return Response(
                    content=await response.read(),
                    status_code=response.status,
                    headers=response_headers,
                )

        except Exception as error:
            # del self.workers[self.subdomain] and stop?
            logger.exception("failed to run worker")
            return PlainTextResponse(str(error), 500)
        finally:
            wk.active_requests -= 1
            wk.idle = time.time()
            if wk.active_requests == 0:
                asyncio.create_task(self.idle_timer(self.subdomain, wk))


@app.command()
def serve(
    http_address: Annotated[
        str, typer.Option("--addr", "-a", help="bind address to listen on")
    ] = state["http_address"]
):
    """
    Start fishweb server
    """
    state["http_address"] = http_address
    host, port = http_address.split(":")

    app = Starlette(
        routes=[Route("/", Root)],
    )
    app.add_middleware(SubdomainMiddleware)

    uvicorn.run(app, host=host, port=int(port))
    # raise typer.Exit()
