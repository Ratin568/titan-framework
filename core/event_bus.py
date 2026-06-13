"""
Event Bus system - all modules communicate through this
"""

import asyncio
from typing import Dict, List, Any, Callable, Awaitable, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger("EventBus")


@dataclass
class Event:
    """Every event in the system"""
    name: str
    source: str
    data: Any
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    event_id: str = field(default_factory=lambda: f"{datetime.now().timestamp()}")


class EventBus:
    """Central Event Bus"""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._async_subscribers: Dict[str, List[Callable[[Event], Awaitable[None]]]] = {}
        self._event_history: List[Event] = []
        self._max_history = 1000
        self._logger = logging.getLogger("EventBus")
    
    def subscribe(self, event_name: str, callback: Callable):
        """Simultaneous sharing"""
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        self._subscribers[event_name].append(callback)
        self._logger.debug(f"Subscribed to {event_name}")
    
    def subscribe_async(self, event_name: str, callback: Callable[[Event], Awaitable[None]]):
        """Asynchronous Sharing"""
        if event_name not in self._async_subscribers:
            self._async_subscribers[event_name] = []
        self._async_subscribers[event_name].append(callback)
        self._logger.debug(f"Async subscribed to {event_name}")
    
    def on(self, event_name: str):
        """Decorator for easier Event Handler registration"""
        def decorator(func):
            self.subscribe_async(event_name, func)
            return func
        return decorator
    
    def unsubscribe(self, event_name: str, callback: Callable):
        """Unsubscribe"""
        if event_name in self._subscribers:
            if callback in self._subscribers[event_name]:
                self._subscribers[event_name].remove(callback)
        
        if event_name in self._async_subscribers:
            if callback in self._async_subscribers[event_name]:
                self._async_subscribers[event_name].remove(callback)
    
    async def publish(self, event: Event):
        """Publish an event"""
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
        
        self._logger.debug(f"Event published: {event.name} from {event.source}")
        
        if event.name in self._subscribers:
            for callback in self._subscribers[event.name]:
                try:
                    callback(event)
                except Exception as e:
                    self._logger.error(f"Error in subscriber {callback}: {e}")
        
        if event.name in self._async_subscribers:
            tasks = []
            for callback in self._async_subscribers[event.name]:
                tasks.append(asyncio.create_task(callback(event)))
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    def get_history(self, event_name: str = None, limit: int = 100) -> List[Event]:
        """Get Event History"""
        if event_name:
            return [e for e in self._event_history if e.name == event_name][-limit:]
        return self._event_history[-limit:]
    
    def clear_history(self):
        """Clear history"""
        self._event_history.clear()
    
    def get_subscriber_count(self, event_name: str = None) -> dict:
        """Get subscriber count"""
        if event_name:
            return {
                "sync": len(self._subscribers.get(event_name, [])),
                "async": len(self._async_subscribers.get(event_name, []))
            }
        
        total_sync = sum(len(v) for v in self._subscribers.values())
        total_async = sum(len(v) for v in self._async_subscribers.values())
        
        return {
            "total_sync": total_sync,
            "total_async": total_async,
            "events": list(self._subscribers.keys()) + list(self._async_subscribers.keys())
        }