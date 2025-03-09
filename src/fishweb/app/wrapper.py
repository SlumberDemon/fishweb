import os
import re
import runpy
import sys
import time
from abc import ABC, abstractmethod
from http import HTTPStatus
from pathlib import Path

from loguru import logger as global_logger
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.staticfiles import StaticFiles
from starlette.types import ASGIApp, Receive, Scope, Send

from fishweb.app.config import AppConfig, AppType
from fishweb.logging import APP_LOG_FORMAT, DEFAULT_LOG_PATH, app_logging_filter

try:
    from watchdog.events import (
        EVENT_TYPE_CLOSED,
        FileSystemEvent,
        FileSystemEventHandler,
    )
    from watchdog.observers import Observer

    watchdog_available = True

    class ReloadHandler(FileSystemEventHandler):
        def __init__(self, app_wrapper: "AsgiAppWrapper", /) -> None:
            self.app_wrapper = app_wrapper

        def on_any_event(self, event: FileSystemEvent) -> None:
            # BUG: Editing a file in VSCode on Windows can trigger 2 events.
            if event.event_type != EVENT_TYPE_CLOSED:
                self.app_wrapper.reload()

except ImportError:
    watchdog_available = False
    Observer = None

try:
    from asgiref.wsgi import WsgiToAsgi
except ImportError:
    WsgiToAsgi = None


BLOCKED_PATH_PATTERNS = {
    re.compile(r"/?\.env.*", re.IGNORECASE),
    re.compile(r"/?fishweb\.ya?ml/?", re.IGNORECASE),
    re.compile(r"/?__pycache__/.*", re.IGNORECASE),
    re.compile(r"/?\.venv.*", re.IGNORECASE),
}


class AppStartupError(Exception):
    def __init__(self, path: Path, *args: object) -> None:
        super().__init__(*args)
        self.path = path


class AppWrapper(ABC):
    def __init__(self, app_dir: Path, /, *, config: AppConfig) -> None:
        self.app_dir = app_dir
        self.config = config
        self.name = app_dir.name
        self.created_at = time.time()
        self.logger = global_logger.bind(app=self.name)
        log_path = DEFAULT_LOG_PATH / self.name / f"{self.name}.log"
        self.logger.add(
            log_path,
            format=APP_LOG_FORMAT,
            rotation="10 MB",
            retention="28 days",
            filter=app_logging_filter(self.name),
        )
        self.logger.add(
            sys.stderr,
            format=APP_LOG_FORMAT,
            backtrace=False,
            diagnose=False,
            filter=app_logging_filter(self.name),
        )

    @property
    @abstractmethod
    def app(self) -> ASGIApp: ...


class StaticAppWrapper(AppWrapper):
    def __init__(self, app_dir: Path, /, *, config: AppConfig) -> None:
        super().__init__(app_dir, config=config)
        self._staticfiles = StaticFiles(directory=app_dir, html=True)

    async def _app(self, scope: Scope, receive: Receive, send: Send) -> None:
        request = Request(scope)
        if any(re.fullmatch(pattern, request.url.path) for pattern in BLOCKED_PATH_PATTERNS):
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
        return await self._staticfiles(scope, receive, send)

    @property
    def app(self) -> ASGIApp:
        return self._app


class AsgiAppWrapper(AppWrapper):
    def __init__(self, app_dir: Path, /, *, config: AppConfig, reload: bool = False) -> None:
        super().__init__(app_dir, config=config)
        self._app = None
        if self.config.reload or reload:
            if watchdog_available and Observer:
                self._handler = ReloadHandler(self)
                self._observer = Observer()
                self._observer.schedule(event_handler=self._handler, path=app_dir, recursive=True)
                self._observer.start()
                self.logger.debug(f"watching {app_dir} for changes")
            else:
                self.logger.warning("watchdog is not installed, live reloading is disabled")
                self.logger.warning(
                    (
                        "install fishweb with the 'reload' extra to enable live reloading: "
                        "uv tool install fishweb[reload]"
                    ),
                )

    @property
    def app(self) -> ASGIApp:
        if self._app is None:
            self._app = self._try_import()
        return self._app

    def reload(self) -> None:
        self.logger.debug(f"reloading app '{self.name}' from {self.app_dir}")
        self.config = AppConfig.load_from_dir(self.app_dir)
        self._app = self._try_import()

    def _try_import(self) -> ASGIApp:
        self.logger.debug(f"loading app '{self.name}'")
        module, app_name = self.config.entry.split(":", maxsplit=1)
        module_path = self.app_dir.joinpath(module.replace(".", "/")).with_suffix(".py")

        original_sys_path = sys.path.copy()
        venv_path = self.app_dir / self.config.venv_path
        sys.path = [
            str(self.app_dir),
            str(venv_path),
            str(venv_path / "lib" / "site-packages"),
            str(venv_path / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"),
            *sys.path,
        ]

        os.environ["FISHWEB_DATA_DIR"] = str(self.app_dir / "data")
        os.environ["FISHWEB_APP_NAME"] = str(self.name)

        try:
            self.logger.debug(f"executing module {module_path}")
            namespace = runpy.run_path(str(module_path))
            try:
                return namespace[app_name]
            except KeyError as exc:
                msg = f"'{app_name}' callable not found in module {module_path}"
                self.logger.error(msg)  # noqa: TRY400
                raise AppStartupError(module_path, msg) from exc
        except Exception as exc:
            if isinstance(exc, AppStartupError):
                raise
            msg = f"failed to execute module {module_path}"
            self.logger.error(msg)  # noqa: TRY400
            raise AppStartupError(module_path, msg) from exc
        finally:
            sys.path = original_sys_path


class WsgiAppWrapper(AsgiAppWrapper):
    def _try_import(self) -> ASGIApp:
        if WsgiToAsgi is None:
            msg = "asgiref is not installed, WSGI apps are not supported, reinstall fishweb as 'fishweb[wsgi]'"
            raise AppStartupError(self.app_dir, msg)
        return WsgiToAsgi(super()._try_import())


def create_app_wrapper(app_dir: Path, /, *, reload: bool = False) -> AppWrapper:
    config = AppConfig.load_from_dir(app_dir)
    if config.app_type is AppType.STATIC:
        return StaticAppWrapper(app_dir, config=config)
    if config.app_type is AppType.ASGI:
        return AsgiAppWrapper(app_dir, config=config, reload=reload)
    if config.app_type is AppType.WSGI:
        return WsgiAppWrapper(app_dir, config=config, reload=reload)
    msg = f"unknown app type: {config.app_type}"
    raise ValueError(msg)
