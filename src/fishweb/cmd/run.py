from pathlib import Path
from typing import Annotated

import httpx
from httpx_retries import Retry, RetryTransport
from rich import print
from typer import Argument, Option, Typer

from fishweb.app import DEFAULT_ROOT_DIR

run_cli = Typer()


def get_app_list(root_dir: Path) -> list[str]:
    return [dir.name for dir in root_dir.iterdir() if dir.is_dir()] if root_dir.is_dir() else []


@run_cli.command()
def run(
    app: Annotated[
        str,
        Argument(autocompletion=lambda: get_app_list(DEFAULT_ROOT_DIR), help="name of the app/folder"),
    ],
    *,
    job: Annotated[str, Option("--job", "-j", help="name of the job to run")],
    root_dir: Annotated[Path, Option("--root", "-r", help="root directory to search for apps")] = DEFAULT_ROOT_DIR,
    fishweb_url: Annotated[
        str,
        Option("--url", "-u", help="url fishweb is on"),
    ] = "localhost:8888",  # (TODO): get from global config?
) -> None:
    """
    Run a process cron job
    """
    # (TODO) add `crons` command to get details of cron jobs
    # (TODO) sofa: add a sorta test mode to allow running crons without fishweb server
    # (TODO) sofa: handle static app not supported with dedicated error log

    retry = Retry(total=5, backoff_factor=0.5)
    transport = RetryTransport(retry=retry)

    with httpx.Client(transport=transport) as client:
        try:
            connection_test = client.head(f"http://{fishweb_url}")
            connection_test.raise_for_status()

            status = 200
            if connection_test.status_code == status:
                url = f"http://{app}.{fishweb_url}/_fishweb/crons"
                client.post(url=url, json={"job": "hi"})

                print(f"ran {app} cron {job}")

        except httpx.HTTPError:
            print("no running fishweb instance found")
