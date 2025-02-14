from typing import Annotated

from typer import Typer, Argument, Option
from fishweb.app import DEFAULT_ROOT_DIR
from pathlib import Path

cron_cli = Typer()


def get_app_list(root_dir: Path) -> list[str]:
    return [dir.name for dir in root_dir.iterdir() if dir.is_dir()] if root_dir.is_dir() else []


@cron_cli.command()
def cron(
    app: Annotated[str, Argument(autocompletion=lambda: get_app_list(DEFAULT_ROOT_DIR))],
    *,
    job: Annotated[str, Option("--job", "-j", help="name of the job to run")],  # autocomplete job?
) -> None:
    """
    Run a cron job
    """
    pass
