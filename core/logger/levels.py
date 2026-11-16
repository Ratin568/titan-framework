
"""
Titan Logger - Log Levels

Defines the standard log levels used by Titan.
"""

from enum import IntEnum


class LogLevel(IntEnum):
    """
    Available logging levels.

    Higher values represent more severe events.
    """

    DEBUG = 10
    INFO = 20
    SUCCESS = 25
    WARNING = 30
    AUDIT = 35
    ERROR = 40
    CRITICAL = 50


# Public aliases for convenient imports.
DEBUG = LogLevel.DEBUG
INFO = LogLevel.INFO
SUCCESS = LogLevel.SUCCESS
WARNING = LogLevel.WARNING
AUDIT = LogLevel.AUDIT
ERROR = LogLevel.ERROR
CRITICAL = LogLevel.CRITICAL


def get_level(value: str | int | LogLevel) -> LogLevel:
    """
    Convert a string or integer into a LogLevel.

    Examples:
        get_level("INFO")
        get_level(20)
        get_level(LogLevel.ERROR)
    """

    if isinstance(value, LogLevel):
        return value

    if isinstance(value, int):
        try:
            return LogLevel(value)
        except ValueError:
            raise ValueError(f"Invalid log level value: {value}") from None

    if isinstance(value, str):
        name = value.strip().upper()

        try:
            return LogLevel[name]
        except KeyError:
            raise ValueError(f"Unknown log level: {value}") from None

    raise TypeError(
        "Log level must be a string, integer, or LogLevel."
    )
