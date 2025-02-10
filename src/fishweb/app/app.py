from http import HTTPStatus
from pathlib import Path

from loguru import logger
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from fishweb.app.wrapper import AppWrapper

DEFAULT_ROOT_DIR = Path.home() / "fishweb"


class SubdomainMiddleware:
    def __init__(self, app: ASGIApp, *, bind_address: str, root_dir: Path) -> None:
        self.app = app
        self.bind_address = bind_address
        self.root_dir = root_dir
        self.app_wrappers: dict[str, AppWrapper] = {}

    def get_app_wrapper(self, subdomain: str) -> AppWrapper:
        wrapper = self.app_wrappers.get(subdomain)

        # TODO(lemonyte): Use watchfiles or something for changes, as directory mtime does not reflect file changes.
        if wrapper and wrapper.get_app_mtime() < wrapper.created_at:
            logger.debug(
                f"reusing {subdomain} app, created_at: {wrapper.created_at:.0f}, mtime: {wrapper.get_app_mtime():.0f}",
            )
            return wrapper

        wrapper = AppWrapper(self.root_dir / subdomain)
        logger.debug(f"starting {subdomain} app")
        self.app_wrappers[subdomain] = wrapper
        return wrapper

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request = Request(scope)
        address = request.headers.get("host") or ""
        subdomain = "www" if address == self.bind_address else address.split(".")[0]
        app_dir = self.root_dir / subdomain

        # Prevent requests outside of the root directory or to the root directory itself,
        # e.g. "http://.localhost:8888"
        if app_dir.parent != self.root_dir:
            response = PlainTextResponse(
                content=HTTPStatus.NOT_FOUND.phrase,
                status_code=HTTPStatus.NOT_FOUND,
            )
            return await response(scope, receive, send)
        if not app_dir.exists():
            logger.warning(f"{subdomain} not found")
            if subdomain == "www":
                # TODO(lemonyte): Include a link to the docs perhaps?
                response = PlainTextResponse(content="Fishweb is running!")
            else:
                response = PlainTextResponse(
                    content=f"{subdomain} Not Found",
                    status_code=HTTPStatus.NOT_FOUND,
                )
            return await response(scope, receive, send)

        # TODO(lemonyte): Properly implement logging including labels for each app.

        # log_path = Path(user_cache_dir("fishweb")).joinpath("domains", subdomain)
        # logger.add(
        #     f"{log_path}/logs.log",
        #     rotation="100 MB",
        #     retention="28 days",
        # )  # compression="zip"

        wrapper = self.get_app_wrapper(subdomain)
        app = wrapper.try_import()
        if not app:
            response = PlainTextResponse(
                content=HTTPStatus.INTERNAL_SERVER_ERROR.phrase,
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            )
            return await response(scope, receive, send)
        return await app(scope, receive, send)


def create_fishweb_app(*, bind_address: str, root_dir: Path) -> Starlette:
    middleware = (Middleware(SubdomainMiddleware, bind_address=bind_address, root_dir=root_dir),)
    return Starlette(middleware=middleware)
