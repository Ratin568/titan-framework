
"""
Titan Logger - Configuration
"""

from dataclasses import dataclass
from pathlib import Path

from .levels import LogLevel, get_level


@dataclass
class LoggerConfig:
    level: LogLevel = LogLevel.INFO
    console: bool = True
    file: bool = False
    file_path: Path = Path("logs/titan.log")
    encoding: str = "utf-8"
    max_bytes: int = 5 * 1024 * 1024
    backup_count: int = 5
    timestamp_format: str = "%Y-%m-%d %H:%M:%S"

    @classmethod
    def from_dict(cls, data: dict | None = None):
        data = data or {}

        return cls(
            level=get_level(data.get("level", "INFO")),
            console=bool(data.get("console", True)),
            file=bool(data.get("file", False)),
            file_path=Path(
                data.get("file_path", "logs/titan.log")
            ),
            encoding=data.get("encoding", "utf-8"),
            max_bytes=max(1024, int(data.get(
                "max_bytes", 5 * 1024 * 1024
            ))),
            backup_count=max(0, int(data.get("backup_count", 5))),
            timestamp_format=data.get(
                "timestamp_format",
                "%Y-%m-%d %H:%M:%S"
            ),
        )
