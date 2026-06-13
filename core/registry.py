"""
Module Registration System
Each module has a register.json file that specifies which files should be executed
"""

import json
import importlib
import inspect
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

from .event_bus import Event, EventBus

logger = logging.getLogger("ModuleRegistry")


class ModuleRegistry:
    """
    The module registrar
    reads the register.json file of each module and executes the declared files
    """
    
    def __init__(self, bot, event_bus: EventBus, service_container):
        self.bot = bot
        self.event_bus = event_bus
        self.services = service_container
        self.modules_path = Path("modules")
        self.loaded_modules: Dict[str, dict] = {}
        self._logger = logging.getLogger("ModuleRegistry")
    
    async def register_all_modules(self):
        """Find and register all modules"""
        if not self.modules_path.exists():
            self.modules_path.mkdir()
            self._logger.warning("Modules folder created, no modules found")
            return
        
        for module_dir in self.modules_path.iterdir():
            if not module_dir.is_dir():
                continue
            if module_dir.name.startswith("__") or module_dir.name.startswith("."):
                continue
            
            await self._register_module(module_dir)
    
    async def _register_module(self, module_path: Path):
        """Register a specific module"""
        module_name = module_path.name
        register_file = module_path / "register.json"
        
        if not register_file.exists():
            self._logger.warning(f"⚠️ Module '{module_name}' has no register.json, skipping...")
            return
        
        # Read registry file
        try:
            with open(register_file, "r", encoding="utf-8") as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            self._logger.error(f"Invalid JSON in {register_file}: {e}")
            return
        
        # Basic module information
        module_info = {
            "name": module_name,
            "path": module_path,
            "config": config,
            "enabled": config.get("enabled", True),
            "exports": config.get("exports", []),
            "requires": config.get("requires", []),
            "handlers": [],
            "loaded_files": []
        }
        
        if not module_info["enabled"]:
            self._logger.info(f"⏸ Module '{module_name}' is disabled")
            return
        
        try:
            # Load the files specified in register.json
            files_to_load = config.get("files", [])
            
            for file_path in files_to_load:
                full_path = module_path / file_path
                if not full_path.exists():
                    self._logger.warning(f"   File not found: {file_path}")
                    continue
                
                # Convert path to module name (e.g. handlers/balance.py -> handlers.balance)
                module_import_name = file_path.replace('/', '.').replace('\\', '.').replace('.py', '')
                
                # Import file
                spec = importlib.util.spec_from_file_location(
                    f"modules.{module_name}.{module_import_name}",
                    full_path
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                module_info["loaded_files"].append(file_path)
                
                # 1. setup_module function (if any)
                if hasattr(module, "setup_module"):
                    if inspect.iscoroutinefunction(module.setup_module):
                        await module.setup_module(self.bot, self.event_bus, self.services)
                    else:
                        module.setup_module(self.bot, self.event_bus, self.services)
                    self._logger.info(f"   ✅ Called setup_module from {file_path}")
                
                # 2. Register handlers function (if any)
                if hasattr(module, "register_handlers"):
                    handlers = module.register_handlers(self.event_bus, self.services)
                    if handlers:
                        module_info["handlers"].extend(handlers)
                    self._logger.info(f"   📡 Registered {len(handlers) if handlers else 0} handlers from {file_path}")
                
                # 3. Any other function specified in config
                for func_name in config.get("call_functions", []):
                    if hasattr(module, func_name):
                        func = getattr(module, func_name)
                        if inspect.iscoroutinefunction(func):
                            await func(self.bot, self.event_bus, self.services)
                        else:
                            func(self.bot, self.event_bus, self.services)
                        self._logger.info(f"   🔧 Called {func_name} from {file_path}")
            
            # Register the module
            self.loaded_modules[module_name] = module_info
            
            # Announce the module loaded event
            await self.event_bus.publish(Event(
                name="module.loaded",
                source="core",
                data={
                    "module": module_name,
                    "config": config,
                    "files_loaded": len(module_info["loaded_files"])
                }
            ))
            
            self._logger.info(f"✅ Module '{module_name}' registered successfully")
            
        except Exception as e:
            self._logger.error(f"❌ Failed to register module '{module_name}': {e}")
            import traceback
            traceback.print_exc()
    
    async def reload_module(self, module_name: str) -> bool:
        """ریلود یک ماژول"""
        if module_name not in self.loaded_modules:
            self._logger.error(f"Module '{module_name}' not found")
            return False
        
        module_info = self.loaded_modules[module_name]
        module_path = module_info["path"]
        
        # Clear from importlib cache
        importlib.invalidate_caches()
        
        # Remove from loaded modules
        del self.loaded_modules[module_name]
        
        # Reload
        await self._register_module(module_path)
        
        # Reload event announcement
        await self.event_bus.publish(Event(
            name="module.reloaded",
            source="core",
            data={"module": module_name}
        ))
        
        self._logger.info(f"🔄 Module '{module_name}' reloaded")
        return True
    
    def get_module(self, name: str) -> Optional[dict]:
        """Get information about a module"""
        return self.loaded_modules.get(name)
    
    def list_modules(self) -> List[str]:
        """List of all loaded modules"""
        return list(self.loaded_modules.keys())
    
    def disable_module(self, module_name: str) -> bool:
        """Disabling a module"""
        if module_name not in self.loaded_modules:
            return False
        
        self.loaded_modules[module_name]["enabled"] = False
        self._logger.info(f"🔴 Module '{module_name}' disabled")
        return True
    
    def enable_module(self, module_name: str) -> bool:
        """Activating a module"""
        if module_name not in self.loaded_modules:
            return False
        
        self.loaded_modules[module_name]["enabled"] = True
        self._logger.info(f"🟢 Module '{module_name}' enabled")
        return True