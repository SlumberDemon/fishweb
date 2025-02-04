from shlex import join
import shutil
import socket
import subprocess
import time
from pathlib import Path

from loguru import logger


class Worker:
    def __init__(self) -> None:
        self.command: subprocess.Popen
        self.active_requests: int = 0
        self.running: bool = False
        self.started_at: float
        self.idle: float
        self.mtime = None
        self.port = None

    def get_app_mtime(self, app: str) -> float:
        app_dir = Path.home().joinpath("fishweb", app)
        return app_dir.stat().st_mtime

    def start(self, app_dir: Path):
        if self.running:
            return self.port

        self.port = self.get_free_port()
        uv = self.locate_uv()

        cmd = [
            uv,
            "run",
        ]
        if app_dir.joinpath("requirements.txt").exists():
            cmd.extend(
                [
                    "--with-requirements",
                    "requirements.txt",
                ]
            )
        if app_dir.joinpath(".env").exists():
            cmd.extend(["--env-file", ".env"])
        cmd.extend(
            [
                "uvicorn",
                "main:app",
                "--port",
                str(self.port),
                "--host",
                "localhost",
                "--ws",
                "none",
                "--lifespan",
                "off",
                "--timeout-keep-alive",
                "30",
            ]
        )

        process = subprocess.Popen(
            cmd,
            text=True,
            cwd=str(app_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.command = process

        start = time.time()
        while time.time() - start < 5:
            if process.poll() is not None:
                _, stderr = process.communicate()
                logger.error(f"process failed: \n {stderr}")
                return None

            try:
                with socket.create_connection(("localhost", self.port), timeout=1):
                    logger.success(f"application {self.port} running")
                    self.started_at = time.time()
                    self.running = True
                    return self.port
            except (socket.error, socket.timeout):
                logger.debug(f"waiting for port {self.port}...")
                time.sleep(0.5)
                continue

        self.stop()
        self.active_requests -= 1
        logger.warning("process failed")
        return None

    def stop(self) -> None:
        if self.running == False:
            return None

        try:
            self.command.terminate()
            time.sleep(0.5)

            if self.command.poll() is None:
                self.command.kill()
                self.command.wait(timeout=5)

        except:
            logger.exception("failed to stop process")
        finally:
            self.running = False

    def get_free_port(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
                server.bind(("", 0))
                server.listen(1)
                return server.getsockname()[1]
        except:
            logger.exception("no free ports available")
            return None

    def locate_uv(self) -> str:
        uv_path = shutil.which("uv")
        if uv_path:
            return uv_path

        uv_paths = [
            Path.home().joinpath(".local", "bin", "uv"),
            "/usr/local/bin/uv",
            "/opt/homebrew/bin/uv",
        ]

        for path in uv_paths:
            if Path(path).exists():
                return str(path)

        logger.error("uv executable not found")
        return ""
