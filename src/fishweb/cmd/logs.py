from pathlib import Path
from typing import Annotated

from rich import print
from typer import Argument, Option, Typer

from fishweb.app import DEFAULT_ROOT_DIR
from fishweb.logging import DEFAULT_LOG_PATH

logs_cli = Typer()


def get_app_list(root_dir: Path) -> list[str]:
    return [dir.name for dir in root_dir.iterdir() if dir.is_dir()] if root_dir.is_dir() else []


def get_app_logs(app: str) -> str:
    log_path = DEFAULT_LOG_PATH / app / f"{app}.log"
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
            print(f"[reverse blue]{found_app} logs[/reverse blue]\n{logs}")
    else:
        logs = get_app_logs(app)
        print(logs)
