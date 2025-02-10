from __future__ import annotations

import runpy
import sys
import time
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from pathlib import Path

    from starlette.types import ASGIApp


class AppWrapper:
    def __init__(self, app_dir: Path) -> None:
        self.app_dir = app_dir
        self.created_at = time.time()
        self.app: ASGIApp | None = None

    def try_import(self) -> ASGIApp | None:
        if self.app:
            return self.app

        original_sys_path = sys.path.copy()
        venv_path = self.app_dir / ".venv"
        sys.path = [
            str(self.app_dir),
            str(venv_path),
            str(venv_path / "lib" / "site-packages"),
            *sys.path,
        ]

        try:
            logger.debug(f"executing module 'main' from {self.app_dir}")
            namespace = runpy.run_path(str(self.app_dir / "main.py"))
            self.app = namespace["app"]
        except ImportError:
            logger.error(f"failed to execute module {self.app_dir / 'main'}")
        except KeyError:
            logger.error(f"app not found in module {self.app_dir / 'main'}")
        finally:
            sys.path = original_sys_path
        return self.app

    def get_app_mtime(self) -> float:
        return self.app_dir.stat().st_mtime
