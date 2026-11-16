
"""
Titan Logger - Formatters
"""

import json
from datetime import timezone

from .record import LogRecord


class TextFormatter:
    """Human-readable log formatter."""

    def __init__(self, timestamp_format="%Y-%m-%d %H:%M:%S"):
        self.timestamp_format = timestamp_format

    def format(self, record: LogRecord) -> str:
        timestamp = record.timestamp.astimezone().strftime(
            self.timestamp_format
        )

        level = record.level.name
        name = record.logger_name

        line = (
            f"{timestamp} | "
            f"{level:<8} | "
            f"{name} | "
            f"{record.message}"
        )

        if record.context:
            context = " ".join(
                f"{key}={value!r}"
                for key, value in record.context.items()
            )
            line += f" | {context}"

        if record.exception:
            line += f"\n{record.exception}"

        return line


class JSONFormatter:
    """Structured JSON formatter."""

    def format(self, record: LogRecord) -> str:
        return json.dumps(
            record.to_dict(),
            ensure_ascii=False,
            default=str
        )
