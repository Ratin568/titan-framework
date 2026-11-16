
"""
Titan Logger - Logging Engine
"""

import sys
import threading
from typing import Iterable

from .config import LoggerConfig
from .levels import LogLevel
from .record import LogRecord
from .handlers import BaseHandler


class LoggerEngine:
    """Processes and distributes log records."""

    def __init__(
        self,
        config: LoggerConfig | None = None,
        handlers: Iterable[BaseHandler] | None = None
    ):
        self.config = config or LoggerConfig()
        self.handlers: list[BaseHandler] = list(handlers or [])
        self._lock = threading.RLock()
        self._closed = False

    def add_handler(self, handler: BaseHandler) -> None:
        if not isinstance(handler, BaseHandler):
            raise TypeError("handler must inherit from BaseHandler")

        with self._lock:
            if self._closed:
                raise RuntimeError("Logger engine is closed")

            self.handlers.append(handler)

    def remove_handler(self, handler: BaseHandler) -> bool:
        with self._lock:
            if handler not in self.handlers:
                return False

            self.handlers.remove(handler)
            handler.close()
            return True

    def set_level(self, level: str | int | LogLevel) -> None:
        from .levels import get_level

        self.config.level = get_level(level)

    def log(
        self,
        level: LogLevel,
        message: str,
        logger_name: str = "Titan",
        context: dict | None = None,
        exception: str | None = None
    ) -> LogRecord | None:

        if self._closed:
            return None

        if level < self.config.level:
            return None

        record = LogRecord(
            level=level,
            message=str(message),
            logger_name=logger_name,
            context=context or {},
            exception=exception
        )

        with self._lock:
            handlers = tuple(self.handlers)

        for handler in handlers:
            try:
                handler.emit(record)
            except Exception:
                # A broken output must never crash the application.
                try:
                    sys.stderr.write(
                        "[Titan Logger] A handler failed:\n"
                    )
                    import traceback
                    traceback.print_exc(file=sys.stderr)
                except Exception:
                    pass

        return record

    def close(self) -> None:
        with self._lock:
            if self._closed:
                return

            self._closed = True
            handlers = tuple(self.handlers)
            self.handlers.clear()

        for handler in handlers:
            try:
                handler.close()
            except Exception:
                pass
