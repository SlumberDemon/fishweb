import typer

from fishweb.cmd.logs import logs_cli
from fishweb.cmd.serve import serve_cli

cli = typer.Typer(
    help="Web apps like serverless",
    epilog="Use 'fishweb [command] --help' for more information about a command.",
    rich_markup_mode="markdown",
    no_args_is_help=True,
)

cli.add_typer(serve_cli)
cli.add_typer(logs_cli)
