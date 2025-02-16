from __future__ import annotations

import runpy
import sys
import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from crontab import CronSlices, CronTab
from loguru import logger
from starlette.staticfiles import StaticFiles

from fishweb.app.config import AppConfig, AppType

try:
    from watchdog.events import (
        EVENT_TYPE_CLOSED,
        FileSystemEvent,
        FileSystemEventHandler,
    )
    from watchdog.observers import Observer

    watchdog_available = True

    class ReloadHandler(FileSystemEventHandler):
        def __init__(self, app_wrapper: ASGIAppWrapper, /) -> None:
            self.app_wrapper = app_wrapper

        def on_any_event(self, event: FileSystemEvent) -> None:
            # BUG: Editing a file in VSCode on Windows can trigger 2 events.
            if event.event_type != EVENT_TYPE_CLOSED:
                self.app_wrapper.reload()
except ImportError:
    watchdog_available = False
    Observer = None

if TYPE_CHECKING:
    from pathlib import Path

    from starlette.types import ASGIApp


class AppStartupError(Exception):
    def __init__(self, path: Path, *args: object) -> None:
        super().__init__(*args)
        self.path = path


class AppWrapper(ABC):
    def __init__(self, app_dir: Path, /, *, config: AppConfig) -> None:
        self.app_dir = app_dir
        self.name = app_dir.name
        self.created_at = time.time()
        self.config = config

    @property
    @abstractmethod
    def app(self) -> ASGIApp: ...


class StaticAppWrapper(AppWrapper):
    def __init__(self, app_dir: Path, /, *, config: AppConfig) -> None:
        super().__init__(app_dir, config=config)
        self._app = StaticFiles(directory=app_dir, html=True)

    @property
    def app(self) -> ASGIApp:
        return self._app


class ASGIAppWrapper(AppWrapper):
    def __init__(self, app_dir: Path, /, *, config: AppConfig, reload: bool = False) -> None:
        super().__init__(app_dir, config=config)
        self._load_crons()
        self._app: ASGIApp | None = None
        if self.config.reload or reload:
            if watchdog_available and Observer:
                self._handler = ReloadHandler(self)
                self._observer = Observer()
                self._observer.schedule(event_handler=self._handler, path=app_dir, recursive=True)
                self._observer.start()
                logger.debug(f"watching {app_dir} for changes")
            else:
                logger.warning("watchdog is not installed, live reloading is disabled")
                logger.warning(
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
        logger.debug(f"reloading app '{self.name}' from {self.app_dir}")
        self.config = AppConfig.load_from_dir(self.app_dir)
        self._load_crons()
        self._app = self._try_import()

    def _try_import(self) -> ASGIApp:
        logger.debug(f"loading app '{self.name}'")
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

        try:
            logger.debug(f"executing module {module_path}")
            namespace = runpy.run_path(str(module_path))
            try:
                return namespace[app_name]
            except KeyError as exc:
                msg = f"'{app_name}' callable not found in module {module_path}"
                logger.error(msg)
                raise AppStartupError(module_path, msg) from exc
        except Exception as exc:
            if isinstance(exc, AppStartupError):
                raise
            msg = f"failed to execute module {module_path}"
            logger.error(msg)
            raise AppStartupError(module_path, msg) from exc
        finally:
            sys.path = original_sys_path

    def _load_crons(self) -> None:
        logger.debug(f"processing crons for app '{self.name}'")
        crontab = CronTab(tabfile=str(self.app_dir / "fishweb.cron"))
        cron_ids = [cron.id for cron in self.config.crons]

        for cron_item in crontab:
            if cron_item.comment not in cron_ids:
                logger.debug(f"removing cron job '{self.name}/{cron_item.comment}'")
                crontab.remove(cron_item)

        for cron in self.config.crons:
            if not CronSlices.is_valid(cron.interval):
                logger.error(f"invalid interval format for cron '{self.name}/{cron.id}': {cron.interval}")
                continue
            try:
                cron_item = next(crontab.find_comment(cron.id))
                logger.debug(f"updating cron job '{cron.id}'")
            except StopIteration:
                logger.debug(f"creating cron job '{cron.id}'")
                cron_item = crontab.new(
                    command=f"{sys.argv[0]} run {self.name} --job {cron.id}",
                    comment=cron.id,
                )
            cron_item.setall(cron.interval)
        crontab.write()


def create_app_wrapper(app_dir: Path, /, *, reload: bool = False) -> AppWrapper:
    config = AppConfig.load_from_dir(app_dir)
    if config.app_type is AppType.STATIC:
        return StaticAppWrapper(app_dir, config=config)
    if config.app_type is AppType.ASGI:
        return ASGIAppWrapper(app_dir, config=config, reload=reload)
    msg = f"unknown app type: {config.app_type}"
    raise ValueError(msg)
