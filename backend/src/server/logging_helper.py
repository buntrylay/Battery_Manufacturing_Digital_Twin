"""Utility helpers for colourised logging output."""

from __future__ import annotations

import logging
from typing import Optional


_LEVEL_COLOURS: dict[str, str] = {
    "DEBUG": "\033[90m",  # grey
    "INFO": "\033[92m",  # green
    "WARNING": "\033[93m",  # yellow
    "ERROR": "\033[91m",  # red
    "CRITICAL": "\033[95m",  # magenta
}

_RESET_COLOUR = "\033[0m"
_DEFAULT_FORMAT = "%(asctime)s | %(levelname_coloured)s | %(name)s | %(message)s"
_DEFAULT_DATEFMT = "%Y-%m-%d %H:%M:%S"
_DEFAULT_LOGGER_NAME = "battery_plant"


class _ColourFormatter(logging.Formatter):
    """Formatter that injects colour codes into level names."""

    def format(self, record: logging.LogRecord) -> str:
        level = record.levelname
        colour = _LEVEL_COLOURS.get(level, "")
        record.levelname_coloured = f"{colour}{level}{_RESET_COLOUR}" if colour else level
        return super().format(record)


def configure_logging(level: int = logging.INFO) -> None:
    """Configure the root logger with colourised console output."""

    handler = logging.StreamHandler()
    handler.setFormatter(_ColourFormatter(_DEFAULT_FORMAT, _DEFAULT_DATEFMT))

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(level)
    root_logger.addHandler(handler)


def get_logger(name: str = _DEFAULT_LOGGER_NAME) -> logging.Logger:
    """Return a namespaced logger configured with the colour formatter."""
    return logging.getLogger(name)


def _format_message(message: str, component: Optional[str]) -> str:
    if component:
        return f"[{component}] {message}"
    return message


def info(message: str, *, component: Optional[str] = None) -> None:
    get_logger().info(_format_message(message, component))


def warning(message: str, *, component: Optional[str] = None) -> None:
    get_logger().warning(_format_message(message, component))


def error(message: str, *, component: Optional[str] = None) -> None:
    get_logger().error(_format_message(message, component))


def debug(message: str, *, component: Optional[str] = None) -> None:
    get_logger().debug(_format_message(message, component))
