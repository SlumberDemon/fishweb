from pathlib import Path
from typing import Annotated

from platformdirs import user_cache_dir
from typer import Argument, Option, Typer, echo

from fishweb.app import DEFAULT_ROOT_DIR

logs_cli = Typer()


def get_app_list(root_dir: Path) -> list[str]:
    return [dir.name for dir in root_dir.iterdir() if dir.is_dir()] if root_dir.is_dir() else []


def get_app_logs(app: str) -> str:
    log_path = Path(user_cache_dir("fishweb")).joinpath("domains", app, "logs.log")
    if log_path.exists():
        return log_path.read_text()
    return ""


@logs_cli.command(no_args_is_help=True)
def logs(
    app: Annotated[str, Argument(autocompletion=lambda: get_app_list(DEFAULT_ROOT_DIR))] = "",
    *,
    all: Annotated[bool, Option("--all", "-a", help="show logs for all apps")] = False,
    root_dir: Annotated[Path, Option("--root", "-r", help="root directory to search for apps")] = DEFAULT_ROOT_DIR,
) -> None:
    """
    View app logs
    """
    if all:
        for found_app in get_app_list(root_dir):
            logs = get_app_logs(found_app)
            echo(f"[reverse blue]{found_app} logs[/reverse blue]\n{logs}")
    else:
        logs = get_app_logs(app)
        echo(logs)
