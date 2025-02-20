from typing import Annotated

import typer

from fishweb import __version__
from fishweb.cmd.logs import logs_cli
from fishweb.cmd.serve import serve_cli

cli = typer.Typer(
    help="Your personal web app manager",
    epilog="Use 'fishweb [command] --help' for more information about a command.",
    rich_markup_mode="markdown",
    no_args_is_help=True,
)

cli.add_typer(serve_cli)
cli.add_typer(logs_cli)


def version_callback(*, value: bool) -> None:
    if value:
        typer.echo(f"fishweb {__version__}")
        raise typer.Exit


@cli.callback()
def main(
    *,
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-v",
            help="Show the version",
            callback=version_callback,
            is_eager=True,
        ),
    ] = False,
) -> None:
    pass
