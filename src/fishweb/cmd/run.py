from typing import Annotated

from typer import Typer, Argument, Option
from fishweb.app import DEFAULT_ROOT_DIR
from pathlib import Path

run_cli = Typer()


def get_app_list(root_dir: Path) -> list[str]:
    return [dir.name for dir in root_dir.iterdir() if dir.is_dir()] if root_dir.is_dir() else []


@run_cli.command()
def run(
    app: Annotated[str, Argument(autocompletion=lambda: get_app_list(DEFAULT_ROOT_DIR))],
    *,
    job: Annotated[str, Option("--job", "-j", help="name of the job to run")],
) -> None:
    """
    Run a cron job
    """
    # (TODO) add `crons` command to get details of cron jobs
    print(f"Running cron job for app: {app} and job: {job}")  # placeholder
