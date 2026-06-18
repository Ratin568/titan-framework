"""
Titan Core - Heart of the Framework
"""

# ============================================
# 📥 Get Exports from config_loader
# ============================================
from .config_loader import default_config
from .hub import TitanHub
from .events.event_bus import EventBus, Event
from .container.service_container import ServiceContainer
from .registry.priority_registry import PriorityRegistry

# ============================================
# 📋 Final list of exports from JSON file
# ============================================
__all__ = default_config.get_core_exports()