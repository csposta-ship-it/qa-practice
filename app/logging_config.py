
from asyncio.log import logger
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

LOG_DIR = (
    Path.home()
    / "OneDrive"
    / "Desktop"
    / "qa_practice_data"
    / "logs"
)

LOG_FILE = LOG_DIR / "app.log"


def configure_logging():
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("qa_practice")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s: %(message)s"
    )

    file_handler = TimedRotatingFileHandler(
    LOG_FILE,
    when="midnight",
    interval=1,
    backupCount=30,
    encoding="utf-8",
    utc=False,
    delay=True,
    )
    file_handler.suffix = "%Y-%m-%d"

    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    for handler in (file_handler, console_handler):
        handler.setFormatter(formatter)

    return logger
