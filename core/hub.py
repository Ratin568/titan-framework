
"""
Titan Hub
Central framework manager.

Responsible for:
- Initializing core services
- Initializing the Titan Logger
- Registering framework services
- Loading modules
- Managing framework lifecycle
"""

from pathlib import Path
from typing import Optional, List

from .events.event_bus import EventBus, Event
from .container.service_container import ServiceContainer
from .registry.priority_registry import PriorityRegistry
from .logger import (
    Logger,
    LoggerEngine,
    LoggerConfig,
    ConsoleHandler,
    FileHandler,
    TextFormatter,
)
from .config_loader import default_config


class TitanHub:
    def __init__(
        self,
        bot,
        search_paths: Optional[List[Path]] = None,
    ):
        # Main application reference
        self.bot = bot

        # Core components
        self.event_bus = EventBus()
        self.services = ServiceContainer()

        # Initialize logger from framework.json
        logging_data = default_config.get_logging_config()
        self.logger_config = LoggerConfig.from_dict(logging_data)

        formatter = TextFormatter(
            timestamp_format=self.logger_config.timestamp_format
        )

        handlers = []

        if self.logger_config.console:
            handlers.append(
                ConsoleHandler(formatter=formatter)
            )

        if self.logger_config.file:
            handlers.append(
                FileHandler(
                    path=self.logger_config.file_path,
                    formatter=formatter,
                    encoding=self.logger_config.encoding,
                    max_bytes=self.logger_config.max_bytes,
                    backup_count=self.logger_config.backup_count,
                )
            )

        self.logger_engine = LoggerEngine(
            config=self.logger_config,
            handlers=handlers,
        )

        self.logger = Logger(
            engine=self.logger_engine,
            name="Titan",
        )

        # Register core services
        self.services.register("bot", self.bot, singleton=True)
        self.services.register("event_bus", self.event_bus, singleton=True)
        self.services.register("hub", self, singleton=True)
        self.services.register("titan", self, singleton=True)
        self.services.register("logger", self.logger, singleton=True)

        # Resolve module search paths
        if search_paths is None:
            configured_paths = default_config.get_modules_paths()
            search_paths = [
                Path(path) for path in configured_paths
            ]

        # Module registry
        self.registry = PriorityRegistry(
            bot=self.bot,
            event_bus=self.event_bus,
            services=self.services,
            search_paths=search_paths,
        )

        self._is_running = False
        self._is_stopped = False

        self.logger.info(
            "Titan Hub initialized",
            search_paths=[str(path) for path in search_paths],
        )

    async def start(self):
        if self._is_running:
            self.logger.warning("Titan Hub is already running")
            return

        if self._is_stopped:
            raise RuntimeError(
                "Titan Hub has been stopped and cannot be restarted."
            )

        self.logger.info("Starting Titan Hub")
        self._is_running = True

        try:
            await self.registry.register_all_modules()

            load_order = self.registry.get_load_order()

            self.logger.info(
                "Module loading completed",
                modules_count=len(self.registry.loaded_modules),
            )

            for item in load_order:
                self.logger.debug(
                    "Module load order",
                    name=item["name"],
                    priority=item["priority"],
                    path=item.get("path", "unknown"),
                )

            await self.event_bus.publish(
                Event(
                    name="system.ready",
                    source="hub",
                    data={
                        "modules_count": len(self.registry.loaded_modules),
                        "modules": list(self.registry.loaded_modules.keys()),
                    },
                )
            )

            self.logger.success(
                "Titan Hub is ready",
                modules_count=len(self.registry.loaded_modules),
            )

        except Exception:
            self._is_running = False
            self.logger.exception("Titan Hub startup failed")
            raise

    async def stop(self):
        if self._is_stopped:
            return

        self.logger.info("Stopping Titan Hub")

        try:
            if self._is_running:
                await self.event_bus.publish(
                    Event(
                        name="system.shutdown",
                        source="hub",
                        data={},
                    )
                )
        finally:
            self._is_running = False
            self.logger.info("Titan Hub stopped")
            self._is_stopped = True
            self.logger.close()

    def get_module(self, name: str):
        return self.registry.get_module(name)

    def get_service(self, name: str):
        return self.services.get(name)

    async def publish_event(self, event: Event):
        await self.event_bus.publish(event)

    def is_running(self) -> bool:
        return self._is_running

    def get_status(self) -> dict:
        return {
            "running": self._is_running,
            "modules": {
                "count": len(self.registry.loaded_modules),
                "list": list(self.registry.loaded_modules.keys()),
                "by_priority": self.registry.get_modules_by_priority(),
            },
            "services": self.services.list_services(),
            "event_bus": self.event_bus.get_subscriber_count(),
        }
