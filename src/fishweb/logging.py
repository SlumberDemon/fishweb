import sys
from typing import TYPE_CHECKING, Callable

from loguru import logger

if TYPE_CHECKING:
    from loguru import Record

GLOBAL_LOG_FORMAT = (
    "<cyan>{time:YYYY-MM-DD HH:mm:ss}</cyan> | <level>{level: <8}</level> |"
    " <bold><magenta>{extra[app]: <16}</magenta></bold> | {message}"
)
APP_LOG_FORMAT = (
    "<cyan>{time:YYYY-MM-DD HH:mm:ss}</cyan> | <level>{level: <8}</level> |"
    " <bold><cyan>{extra[app]: <16}</cyan></bold> | {message}"
)

def app_logging_filter(app_name: str) -> Callable[["Record"], bool]:
    return lambda record: record["extra"].get("app") == app_name


def configure_logging() -> None:
    # Remove default log handler.
    logger.remove(0)
    logger.add(
        sys.stderr,
        format=GLOBAL_LOG_FORMAT,
        backtrace=False,
        diagnose=False,
        filter=app_logging_filter("<fishweb>"),
    )
    logger.configure(
        extra={"app": "<fishweb>"},
    )
