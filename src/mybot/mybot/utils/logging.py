"""Logging configuration for mybot."""

import logging
import sys

from mybot.utils.config import Config
from logging.handlers import RotatingFileHandler

def setup_logging(config: Config, console_output: bool = False) -> None:
    """Set up logging for mybot."""
    format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(format_str)

    console_format = "%(levelname)s - %(name)s - %(message)s"
    console_formatter = logging.Formatter(console_format)

    root_logger = logging.getLogger("mybot")
    root_logger.setLevel(logging.DEBUG)

    config.logging_path.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        config.logging_path / "mybot.log", maxBytes=256 * 1024 * 128, backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)

    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.INFO)
        root_logger.addHandler(console_handler)
