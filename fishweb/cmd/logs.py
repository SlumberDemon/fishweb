from pathlib import Path

import typer
from platformdirs import user_cache_dir
from rich import print
from typing_extensions import Annotated

app = typer.Typer()


def apps():
    dir = Path.home().joinpath("fishweb")
    if dir.exists():
        return [d.name for d in dir.iterdir() if d.is_dir()]
    return []


def get_app_logs(app: str):
    log_path = Path(user_cache_dir("fishweb")).joinpath("domains", app, "logs.log")
    if log_path.exists():
        with open(log_path) as file:
            return file.read()
    return ""


@app.command(no_args_is_help=True)
def logs(
    app: Annotated[str, typer.Argument(autocompletion=apps)] = "",
    all: Annotated[
        bool, typer.Option("--all", "-a", help="show logs for all apps")
    ] = False,
):
    """
    View app logs
    """
    if all:
        for app in apps():
            logs = get_app_logs(app)
            print(f"[reverse blue]{app} logs[/reverse blue] \n{logs}")

    if not all:
        logs = get_app_logs(app)
        print(logs)
