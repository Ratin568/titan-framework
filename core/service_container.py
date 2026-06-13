"""
Service Container - Manages shared services between modules. Each module can register or receive services.
"""

from typing import Dict, Any, Type, TypeVar, Optional, Callable
import logging

logger = logging.getLogger("ServiceContainer")

T = TypeVar('T')


class ServiceContainer:
    """
    Service Container (similar to Dependency Injection)
    All modules are served from here
    """
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._singletons: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._logger = logging.getLogger("ServiceContainer")
    
    def register(self, name: str, service: Any, singleton: bool = True):
        """
        Register a service
        If singleton=True, an instance is always returned
        """
        if singleton:
            self._singletons[name] = service
            self._logger.info(f"Service registered (singleton): {name}")
        else:
            self._services[name] = service
            self._logger.info(f"Service registered (prototype): {name}")
    
    def register_factory(self, name: str, factory: Callable):
        """Register a factory to create a service at request time"""
        self._factories[name] = factory
        self._logger.info(f"Factory registered: {name}")
    
    def get(self, name: str) -> Optional[Any]:
        """Receive a service"""
        if name in self._singletons:
            return self._singletons[name]
        
        if name in self._factories:
            service = self._factories[name]()
            if hasattr(service, '__singleton__') and service.__singleton__:
                self._singletons[name] = service
            return service
        
        if name in self._services:
            return self._services[name]
        
        self._logger.warning(f"Service not found: {name}")
        return None
    
    def has(self, name: str) -> bool:
        """Checking for service existence"""
        return name in self._singletons or name in self._services or name in self._factories
    
    def register_bot_services(self, bot):
        """Registering Default Bot Services"""
        self.register("bot", bot, singleton=True)
        
        # Register database (if any)
        if hasattr(bot, 'db') and bot.db:
            self.register("db", bot.db, singleton=True)
        
        self._logger.info("Core bot services registered")
    
    def list_services(self) -> dict:
        """List of all services with their types"""
        return {
            "singletons": list(self._singletons.keys()),
            "prototypes": list(self._services.keys()),
            "factories": list(self._factories.keys())
        }
    
    def remove(self, name: str) -> bool:
        """حذف یک سرویس"""
        if name in self._singletons:
            del self._singletons[name]
            return True
        if name in self._services:
            del self._services[name]
            return True
        if name in self._factories:
            del self._factories[name]
            return True
        return False
    
    def clear(self):
        """Clear all services"""
        self._singletons.clear()
        self._services.clear()
        self._factories.clear()
        self._logger.info("All services cleared")