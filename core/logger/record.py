
"""
Titan Logger - Log Record
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from .levels import LogLevel


@dataclass(frozen=True, slots=True)
class LogRecord:
    """Immutable representation of a logging event."""

    level: LogLevel
    message: str
    logger_name: str = "Titan"
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    context: dict[str, Any] = field(default_factory=dict)
    exception: str | None = None
    record_id: str = field(default_factory=lambda: uuid4().hex)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.record_id,
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.name,
            "logger": self.logger_name,
            "message": self.message,
            "context": self.context,
            "exception": self.exception,
        }
