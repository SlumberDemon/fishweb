import sys
from http import HTTPStatus
from pathlib import Path

from loguru import logger as global_logger
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.middleware import Middleware
from starlette.middleware.exceptions import ExceptionMiddleware
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from fishweb.app.wrapper import AppWrapper, create_app_wrapper
from fishweb.logging import GLOBAL_LOG_FORMAT, app_logging_filter

DEFAULT_ROOT_DIR = Path.home() / "fishweb"


def extract_subdomain(hostname: str, /) -> str:
    """Attempt to extract the subdomain from a hostname, including nested subdomains.

    The last two segments are removed, unless the last segment is `localhost`,
    in which case only the last segment is removed.
    If there is no subdomain, `www` is returned.
    """
    segments = hostname.split(".")
    # TODO(lemonyte): #24 Take into account other domain configurations, such as `domain.co.uk`.
    # This should be done by using a user-configured domain that will be used to split the hostname.
    root_levels = 2
    if segments[-1] == "localhost":
        root_levels = 1
    return "www" if len(segments) == root_levels else ".".join(segments[:-root_levels])


class SubdomainMiddleware:
    def __init__(self, app: ASGIApp, *, root_dir: Path, reload: bool = False) -> None:
        self.app = app
        self.root_dir = root_dir
        self.reload = reload
        self.app_wrappers: dict[str, AppWrapper] = {}
        self.logger = global_logger.bind(app="<middleware>")
        self.logger.add(
            sys.stderr,
            format=GLOBAL_LOG_FORMAT,
            backtrace=False,
            diagnose=False,
            filter=app_logging_filter("<middleware>"),
        )
        self.logger.debug(f"initialized middleware serving from {root_dir}")

    def get_app_wrapper(self, subdomain: str) -> AppWrapper:
        wrapper = self.app_wrappers.get(subdomain)
        if not wrapper:
            try:
                wrapper = create_app_wrapper(self.root_dir / subdomain, reload=self.reload)
            except Exception:
                self.logger.exception(f"failed to create wrapper for app '{subdomain}'")
                raise
            self.app_wrappers[subdomain] = wrapper
        return wrapper

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request = Request(scope)
        hostname = request.url.hostname or ""
        subdomain = extract_subdomain(hostname)
        app_dir = self.root_dir / subdomain
        self.logger.debug(f"handling request for subdomain '{subdomain}' on hostname '{hostname}'")

        # Prevent requests outside of the root directory or to the root directory itself,
        # e.g. "http://.localhost"
        if app_dir.parent != self.root_dir:
            self.logger.warning(
                f"subdomain '{subdomain}' ({app_dir}) is outside of the root directory {self.root_dir}",
            )
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
        if not app_dir.exists():
            self.logger.warning(f"app '{subdomain}' not found")
            if subdomain == "www":
                response = PlainTextResponse(
                    content="Fishweb is running! Check out https://fishweb.sofa.sh for next steps.",
                )
            else:
                response = PlainTextResponse(
                    content=f"{subdomain} Not Found",
                    status_code=HTTPStatus.NOT_FOUND,
                )
            return await response(scope, receive, send)

        status_code = HTTPStatus.OK

        async def inner_send(message: Message) -> None:
            if message["type"] == "http.response.start":
                nonlocal status_code
                status_code = message["status"]
            await send(message)

        wrapper = self.get_app_wrapper(subdomain)
        try:
            return await wrapper.app(scope, receive, inner_send)
        except Exception as exc:
            if isinstance(exc, HTTPException):
                status_code = exc.status_code
                raise
            status_code = HTTPStatus.INTERNAL_SERVER_ERROR
            self.logger.exception("failed to handle request", app=subdomain)
            raise
        finally:
            full_request_path = request.url.path + ("?" + request.url.query if request.url.query else "")
            self.logger.info(
                f"{request.method} {full_request_path} {status_code} {HTTPStatus(status_code).phrase}",
                app=subdomain,
            )


def create_fishweb_app(*, root_dir: Path, reload: bool = False) -> ASGIApp:
    middleware = (
        # The ExceptionMiddleware must go before SubdomainMiddleware to properly handle exceptions
        # re-raised by the SubdomainMiddleware.
        Middleware(ExceptionMiddleware),
        Middleware(SubdomainMiddleware, root_dir=root_dir, reload=reload),
    )
    return Starlette(middleware=middleware)
