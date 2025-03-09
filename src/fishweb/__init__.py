import os
from pathlib import Path

from fishweb.app import DEFAULT_ROOT_DIR, create_fishweb_app
from fishweb.logging import configure_logging

configure_logging()

app = create_fishweb_app(
    root_dir=Path(os.getenv("FISHWEB_ROOT_DIR", DEFAULT_ROOT_DIR)),
    reload=bool(os.getenv("FISHWEB_RELOAD")),
)

__all__ = ("app",)
__version__ = "0.2.2"
