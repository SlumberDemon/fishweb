import typer

from .cmd import logs_app, serve_app

app = typer.Typer(
    help="Web apps like serverless",
    epilog="Use 'fishweb [command] --help' for more information about a command.",
    rich_markup_mode="markdown",
    no_args_is_help=True,
)

app.add_typer(serve_app)
app.add_typer(logs_app)
