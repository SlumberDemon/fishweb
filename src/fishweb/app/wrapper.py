import re
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


def create_app_wrapper(app_dir: Path) -> AppWrapper:
    config = AppConfig.load_from_dir(app_dir)
    if config.app_type is AppType.STATIC:
        return StaticAppWrapper(app_dir, config=config)
    msg = f"unknown app type: {config.app_type}"
    raise ValueError(msg)
