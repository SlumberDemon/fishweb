from pathlib import Path
from typing import Annotated

import uvicorn
from typer import Option, Typer

from fishweb.app import DEFAULT_ROOT_DIR, create_fishweb_app

serve_cli = Typer()


@serve_cli.command()
def serve(
    bind_address: Annotated[
        str,
        Option("--addr", "-a", help="bind address to listen on"),
    ] = "localhost:8888",
    root_dir: Annotated[
        Path,
        Option("--root", "-r", help="root directory to serve apps from"),
    ] = DEFAULT_ROOT_DIR,
) -> None:
    """
    Start fishweb server
    """
    host, port = bind_address.split(":")
    app = create_fishweb_app(bind_address=bind_address, root_dir=root_dir)
    # TODO(lemonyte): Make uvicorn dependency optional.
    uvicorn.run(app, host=host, port=int(port))
