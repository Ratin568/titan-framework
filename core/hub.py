import asyncio
import logging

from .event_bus import EventBus, Event
from .service_container import ServiceContainer
from .priority_registry import PriorityRegistry

logger = logging.getLogger("TitanHub")


class TitanHub:
    def __init__(self, bot):
        self.bot = bot
        self.event_bus = EventBus()
        self.services = ServiceContainer()
        self.registry = PriorityRegistry(bot, self.event_bus, self.services)
        
        self.services.register_bot_services(bot)
        self.services.register("event_bus", self.event_bus, singleton=True)
        self.services.register("hub", self, singleton=True)
        
        self._is_running = False
        self._logger = logging.getLogger("TitanHub")
    
    async def start(self):
        self._logger.info("🚀 Starting Titan Hub...")
        self._is_running = True
        
        await self.registry.register_all_modules()
        
        load_order = self.registry.get_load_order()
        self._logger.info(f"📋 Final load order:")
        for item in load_order:
            self._logger.info(f"   [{item['priority']:3d}] {item['name']}")
        
        await self.event_bus.publish(Event(
            name="system.ready",
            source="hub",
            data={
                "modules_count": len(self.registry.loaded_modules),
                "modules": list(self.registry.loaded_modules.keys())
            }
        ))
        
        self._logger.info(f"✅ Titan Hub ready with {len(self.registry.loaded_modules)} modules")
    
    async def stop(self):
        self._logger.info("🛑 Stopping Titan Hub...")
        await self.event_bus.publish(Event(
            name="system.shutdown",
            source="hub",
            data={}
        ))
        self._is_running = False
        self._logger.info("✅ Titan Hub stopped")
    
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
                "by_priority": self.registry.get_modules_by_priority()
            },
            "services": self.services.list_services(),
            "event_bus": self.event_bus.get_subscriber_count()
        }