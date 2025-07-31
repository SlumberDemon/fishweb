from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path
    from typing import IO

    from loguru import Logger

import asyncio
import socket
import subprocess
import sys
import time

from dotenv import dotenv_values
from loguru import logger as global_logger

from fishweb.app.config import AppConfig
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
        def __init__(self, app_process: AppProcess, /) -> None:
            self.app_process = app_process

        def on_any_event(self, event: FileSystemEvent) -> None:
            # BUG: Editing a file in VSCode on Windows can trigger 2 events.
            if event.event_type != EVENT_TYPE_CLOSED:
                self.app_process.reload()

except ImportError:
    watchdog_available = False
    Observer = None


# TODO(sofa): Add reload with watchdog
class ProcessError(Exception):
    def __init__(self, path: Path, *args: object) -> None:
        super().__init__(*args)
        self.path = path


class Process:
    def __init__(self, logger: Logger, cmd: list[str], cwd: Path, env: dict[str, str] | None = None) -> None:
        self._process = None
        self.cmd = cmd
        self.cwd = cwd
        self.env = env
        self.logger = logger

    def start(self) -> subprocess.Popen:
        if self._process is None:
            self._process = subprocess.Popen(  # noqa: S603
                self.cmd,
                cwd=self.cwd,
                env=self.env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            self._logging()
        return self._process

    async def _logging_stream(self) -> None:
        if self._process is None:
            return

        async def read_stream(stream: IO[str], logger) -> None:
            while True:
                line = await asyncio.get_event_loop().run_in_executor(None, stream.readline)
                if not line:
                    break
                logger(line.rstrip())

        stdout = self._process.stdout
        stderr = self._process.stderr
        tasks = []

        # TODO(sofa): see if asyncio.TaskGroup() improves performance

        if stdout:
            tasks.append(asyncio.create_task(read_stream(stdout, self.logger.info)))

        if stderr:
            tasks.append(asyncio.create_task(read_stream(stderr, self.logger.info)))

        self._logging_tasks = tasks
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def _logging(self) -> None:
        if self._process is None:
            return

        self._logging_task = asyncio.create_task(self._logging_stream())

    def stop(self) -> None:
        if self._process is not None:
            if hasattr(self, "_logging_task") and not self._logging_task.done():
                self._logging_task.cancel()
            if hasattr(self, "_logging_tasks"):
                for task in self._logging_tasks:
                    if not task.done():
                        task.cancel()

            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
            self._process = None

    def is_running(self) -> bool:
        return self._process is not None and self._process.poll() is None


class AppProcess:
    def __init__(self, app_dir: Path, /, *, config: AppConfig, reload: bool = False) -> None:
        self.app_dir: Path = app_dir
        self.config: AppConfig = config
        self.name: str = app_dir.name
        self.created_at: float = time.time()
        self.port: int | None = self.config.port
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
        self._process = None
        self._timer_task = None

        if self.config.reload or reload:  # Maybe consider prioritizing reload flag to ensure it's disabled for crons
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

    def app(self) -> Process:
        if self._process is None:
            self._process = self._start_process()
        elif self._process.is_running():
            self.reset_timer()
        return self._process

    def reload(self) -> None:
        self.logger.debug(f"reloading app '{self.name}' from {self.app_dir}")
        self.config = AppConfig.load_from_dir(self.app_dir)

        if self._process is None:
            return

        self._stop_process()

    def _start_process(self) -> Process:
        self.logger.debug(f"starting process '{self.name}'")

        if self.port is None:
            self.port = self._get_free_port()

        run_cmd = self.config.run_cmd.replace("$PORT", f"{self.port}")

        env = {
            "FISHWEB_DATA_DIR": str(self.app_dir / "data"),
            "FISHWEB_APP_NAME": str(self.name),
            **dotenv_values(self.app_dir / ".env"),
        }

        try:
            process = Process(logger=self.logger, cmd=run_cmd.split(), cwd=self.app_dir, env=env)
            process.start()

            self._process = process
            self.reset_timer()

            return process  # noqa: TRY300

        except Exception:
            self.logger.exception(f"failed to start process for '{self.name}'")
            raise

    def _stop_process(self) -> None:
        if self._timer_task and not self._timer_task.done():
            self._timer_task.cancel()
        if self._process:
            self._process.stop()
            self._process = None

    def _get_free_port(self) -> int:
        with socket.socket() as sock:
            sock.bind(("", 0))
            return sock.getsockname()[1]

    def reset_timer(self) -> None:
        self.created_at = time.time()
        if self._timer_task and not self._timer_task.done():
            self._timer_task.cancel()
        self._timer_task = asyncio.create_task(self._idle_timer())

    async def _idle_timer(self) -> None:
        timeout = 30

        try:
            while self._process and self._process.is_running():
                elapsed = time.time() - self.created_at

                if elapsed >= timeout:
                    self.logger.info(f"process '{self.name}' idle timeout")
                    self._stop_process()
                    break
                await asyncio.sleep(30 - elapsed)

        except asyncio.CancelledError:
            pass


def create_app_process(app_dir: Path, /, *, reload: bool = False) -> AppProcess:
    config = AppConfig.load_from_dir(app_dir)

    return AppProcess(app_dir, config=config, reload=reload)
