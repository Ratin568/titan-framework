
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from .base import BaseHandler
from ..formatter import TextFormatter


class FileHandler(BaseHandler):
    def __init__(
        self,
        path,
        formatter=None,
        encoding="utf-8",
        max_bytes=5 * 1024 * 1024,
        backup_count=5,
    ):
        super().__init__(formatter or TextFormatter())

        log_path = Path(path)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        self.handler = RotatingFileHandler(
            filename=str(log_path),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding=encoding,
        )

    def emit(self, record):
        formatted_message = self.formatter.format(record)

        log_record = logging.LogRecord(
            name=record.logger_name,
            level=int(record.level),
            pathname="",
            lineno=0,
            msg=formatted_message,
            args=(),
            exc_info=None,
        )

        self.handler.emit(log_record)

    def close(self):
        self.handler.close()
