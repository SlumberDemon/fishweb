from pathlib import Path
from typing import Annotated

from loguru import logger
from rich import print
from typer import Option, Typer

try:
    import uvicorn
except ImportError:
    uvicorn = None


from fishweb.app import DEFAULT_ROOT_DIR, create_fishweb_app

serve_cli = Typer()


@serve_cli.command()
def serve(
    *,
    host: Annotated[
        str,
        Option("--host", "-h", help="host address to listen on"),
    ] = "localhost",
    port: Annotated[
        int,
        Option("--port", "-p", help="port number to listen on"),
    ] = 8888,
    root_dir: Annotated[
        Path,
        Option("--root", "-r", help="root directory to serve apps from"),
    ] = DEFAULT_ROOT_DIR,
    reload: Annotated[
        bool,
        Option("--reload", "-r", help="enable live reloading"),
    ] = False,
) -> None:
    """
    Start fishweb server
    """
    if uvicorn:
        app = create_fishweb_app(root_dir=root_dir, reload=reload)
        logger.info(f"fishweb server starting on http://{host}:{port}")
        uvicorn.run(app, host=host, port=port, log_level="critical")
    else:
        print("Uvicorn is not installed.")
        print("Install fishweb with the 'serve' extra to use this command.")
        print(r"e.g. [bold blue]uv tool install fishweb\[serve][/bold blue]")
