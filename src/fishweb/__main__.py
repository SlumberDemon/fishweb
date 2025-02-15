from fishweb.cmd import cli
from fishweb.logging import configure_logging

if __name__ == "__main__":
    configure_logging()
    cli()
