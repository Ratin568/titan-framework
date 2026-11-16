
"""
Titan Logger - Public API
"""

import traceback
from typing import Any

from .engine import LoggerEngine
from .levels import LogLevel


class Logger:
    """Simple public interface for Titan logging."""

    def __init__(
        self,
        engine: LoggerEngine,
        name: str = "Titan",
        context: dict[str, Any] | None = None
    ):
        self._engine = engine
        self.name = name
        self._context = dict(context or {})

    def bind(self, **context) -> "Logger":
        """Create a logger with additional context."""

        new_context = {
            **self._context,
            **context
        }

        return Logger(
            engine=self._engine,
            name=self.name,
            context=new_context
        )

    def _log(
        self,
        level: LogLevel,
        message: str,
        exception: str | None = None,
        **context
    ):
        combined_context = {
            **self._context,
            **context
        }

        return self._engine.log(
            level=level,
            message=message,
            logger_name=self.name,
            context=combined_context,
            exception=exception
        )

    def debug(self, message: str, **context):
        return self._log(LogLevel.DEBUG, message, **context)

    def info(self, message: str, **context):
        return self._log(LogLevel.INFO, message, **context)

    def success(self, message: str, **context):
        return self._log(LogLevel.SUCCESS, message, **context)

    def warning(self, message: str, **context):
        return self._log(LogLevel.WARNING, message, **context)

    def audit(self, message: str, **context):
        return self._log(LogLevel.AUDIT, message, **context)

    def error(self, message: str, **context):
        return self._log(LogLevel.ERROR, message, **context)

    def critical(self, message: str, **context):
        return self._log(LogLevel.CRITICAL, message, **context)

    def exception(
        self,
        message: str,
        exc: BaseException | None = None,
        **context
    ):
        if exc is not None:
            exception_text = "".join(
                traceback.format_exception(
                    type(exc), exc, exc.__traceback__
                )
            )
        else:
            exception_text = traceback.format_exc()

        if exception_text.strip() == "NoneType: None":
            exception_text = None

        return self._log(
            LogLevel.ERROR,
            message,
            exception=exception_text,
            **context
        )

    def set_level(self, level: str | int | LogLevel):
        self._engine.set_level(level)

    def add_handler(self, handler):
        self._engine.add_handler(handler)

    def close(self):
        self._engine.close()
