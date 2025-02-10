import os
from pathlib import Path

from fishweb.app import DEFAULT_ROOT_DIR, create_fishweb_app

app = create_fishweb_app(
    root_dir=Path(os.getenv("FISHWEB_ROOT_DIR", DEFAULT_ROOT_DIR)),
)

__all__ = ("app",)
__version__ = "0.1.0"
