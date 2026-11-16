
"""
Titan Logger - Base Handler
"""

from abc import ABC, abstractmethod

from ..record import LogRecord


class BaseHandler(ABC):
    """Base class for all logger output handlers."""

    def __init__(self, formatter=None):
        self.formatter = formatter

    @abstractmethod
    def emit(self, record: LogRecord) -> None:
        """Write one log record to the destination."""
        raise NotImplementedError

    def close(self) -> None:
        """Release handler resources if necessary."""
