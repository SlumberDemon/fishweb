from __future__ import annotations

import os
import runpy
import sys
import time
from typing import TYPE_CHECKING

from loguru import logger

try:
    from watchdog.events import EVENT_TYPE_CLOSED, FileSystemEvent, FileSystemEventHandler
    from watchdog.observers import Observer

    watchdog_available = True

    class ReloadHandler(FileSystemEventHandler):
        def __init__(self, app_wrapper: AppWrapper, /) -> None:
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


class AppWrapper:
    def __init__(self, app_dir: Path, /, *, reload: bool = False) -> None:
        self.app_dir = app_dir
        self.created_at = time.time()
        self._app: ASGIApp | None = None
        if reload:
            if watchdog_available and Observer:
                self._handler = ReloadHandler(self)
                self._observer = Observer()
                self._observer.schedule(event_handler=self._handler, path=app_dir, recursive=True)
                self._observer.start()
                logger.debug(f"watching {app_dir} for changes")
            else:
                logger.warning("watchdog is not installed, hot reloading is disabled")
                logger.warning(
                    (
                        "install fishweb with the 'reload' extra to enable live reloading: "
                        "uv tool install fishweb[reload]"
                    ),
                )

    @property
    def app(self) -> ASGIApp | None:
        if self._app is None:
            self._try_import()
        return self._app

    def reload(self) -> None:
        logger.debug(f"reloading app '{self.app_dir.name}' from {self.app_dir}")
        self._try_import()

    def _try_import(self) -> None:
        logger.debug(f"loading app '{self.app_dir.name}'")
        original_sys_path = sys.path.copy()
        module_path = self.app_dir / "main.py"
        venv_path = self.app_dir / ".venv"
        sys.path = [
            str(self.app_dir),
            str(venv_path),
            str(venv_path / "lib" / "site-packages"),
            *sys.path,
        ]

        try:
            logger.debug(f"executing module {module_path}")
            namespace = runpy.run_path(str(module_path))
            try:
                self._app = namespace["app"]
            except KeyError:
                logger.error(f"'app' callable not found in module {module_path}")
        except Exception as exc:
            msg = f"failed to execute module {module_path}"
            logger.error(msg)
            raise AppStartupError(module_path, msg) from exc
        finally:
            sys.path = original_sys_path

    def get_app_git(self) -> float | None:
        git_path = self.app_dir / ".git"

        if git_path.exists():
            git_head_file = git_path / "HEAD"

            ref_path = git_head_file.open("r").read().split(" ")[1].strip()
            file = self.app_dir / ".git" / ref_path

            return os.path.getmtime(file)
        return None
