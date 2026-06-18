"""
Priority-based Module Registry with recursive folder scanning (Multi-path support)
"""

import json
import importlib
import inspect
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

from ..events.event_bus import Event, EventBus

logger = logging.getLogger("PriorityRegistry")


class PriorityRegistry:
    """Module registry that scans multiple paths recursively for register.json"""

    def __init__(self, bot, event_bus: EventBus, services, search_paths: List[Path]):
        self.bot = bot
        self.event_bus = event_bus
        self.services = services
        self.search_paths = search_paths
        self.loaded_modules: Dict[str, dict] = {}
        self._logger = logging.getLogger("PriorityRegistry")

    async def register_all_modules(self):
        """Find and register all modules recursively from all search paths"""
        modules_list = []

        for base_path in self.search_paths:
            if not base_path.exists():
                continue

            for register_file in base_path.rglob("register.json"):
                module_dir = register_file.parent

                if any(part.startswith("__") or part.startswith(".") for part in module_dir.parts):
                    continue

                try:
                    with open(register_file, "r", encoding="utf-8") as f:
                        config = json.load(f)

                    priority = config.get("priority", 100)
                    enabled = config.get("enabled", True)
                    name = config.get("name", module_dir.name)

                    rel_path = module_dir.relative_to(base_path)

                    modules_list.append({
                        "path": module_dir,
                        "rel_path": str(rel_path),
                        "dir_name": module_dir.name,
                        "name": name,
                        "priority": priority,
                        "enabled": enabled,
                        "config": config,
                        "base_path": base_path
                    })

                    self._logger.debug(f"Found module: {name} at {rel_path} (priority={priority})")

                except json.JSONDecodeError as e:
                    self._logger.error(f"Invalid JSON in {register_file}: {e}")
                    continue

        if not modules_list:
            self._logger.warning("No modules found with register.json in any search path")
            return

        modules_list.sort(key=lambda x: x["priority"])

        self._logger.info(f"📋 Found {len(modules_list)} module(s), loading by priority:")
        for i, mod in enumerate(modules_list, 1):
            self._logger.info(f"   {i}. [{mod['priority']:3d}] {mod['name']} ({mod['rel_path']})")

        for module_info in modules_list:
            if not module_info["enabled"]:
                self._logger.info(f"⏸ Module '{module_info['name']}' is disabled")
                continue

            await self._register_module(module_info)

    async def _register_module(self, module_info: dict):
        """Register a single module"""
        module_path = module_info["path"]
        module_name = module_info["name"]
        rel_path = module_info["rel_path"]
        config = module_info["config"]
        priority = module_info["priority"]

        self._logger.info(f"📦 Loading module: {module_name} (priority={priority}) from {rel_path}")

        loaded_module = {
            "name": module_name,
            "rel_path": rel_path,
            "path": module_path,
            "config": config,
            "priority": priority,
            "enabled": config.get("enabled", True),
            "exports": config.get("exports", []),
            "requires": config.get("requires", []),
            "handlers": [],
            "loaded_files": []
        }

        try:
            files_to_load = config.get("files", [])

            for file_path in files_to_load:
                full_path = module_path / file_path
                if not full_path.exists():
                    self._logger.warning(f"   File not found: {file_path}")
                    continue

                import_name = str(rel_path).replace("/", ".").replace("\\", ".")
                module_import_name = f"{import_name}.{file_path.replace('/', '.').replace('\\', '.').replace('.py', '')}"

                spec = importlib.util.spec_from_file_location(
                    f"modules.{module_import_name}",
                    full_path
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                loaded_module["loaded_files"].append(file_path)

                if hasattr(module, "setup_module"):
                    if inspect.iscoroutinefunction(module.setup_module):
                        await module.setup_module(self.bot, self.event_bus, self.services)
                    else:
                        module.setup_module(self.bot, self.event_bus, self.services)
                    self._logger.info(f"   ✅ Called setup_module from {file_path}")

                if hasattr(module, "register_handlers"):
                    handlers = module.register_handlers(self.event_bus, self.services)
                    if handlers:
                        loaded_module["handlers"].extend(handlers)
                    self._logger.info(f"   📡 Registered {len(handlers) if handlers else 0} handlers")

                for func_name in config.get("call_functions", []):
                    if hasattr(module, func_name):
                        func = getattr(module, func_name)
                        if inspect.iscoroutinefunction(func):
                            await func(self.bot, self.event_bus, self.services)
                        else:
                            func(self.bot, self.event_bus, self.services)
                        self._logger.info(f"   🔧 Called {func_name}")

            self.loaded_modules[module_name] = loaded_module

            await self.event_bus.publish(Event(
                name="module.loaded",
                source="core",
                data={
                    "module": module_name,
                    "path": rel_path,
                    "priority": priority,
                    "files_loaded": len(loaded_module["loaded_files"])
                }
            ))

            self._logger.info(f"✅ Module '{module_name}' registered successfully")

        except Exception as e:
            self._logger.error(f"❌ Failed to register module '{module_name}': {e}")
            import traceback
            traceback.print_exc()

    def get_module(self, name: str) -> Optional[dict]:
        return self.loaded_modules.get(name)

    def list_modules(self) -> List[str]:
        return list(self.loaded_modules.keys())

    def get_modules_by_priority(self) -> Dict[int, List[str]]:
        groups = {}
        for name, info in self.loaded_modules.items():
            priority = info.get("priority", 100)
            if priority not in groups:
                groups[priority] = []
            groups[priority].append(name)
        return dict(sorted(groups.items()))

    def get_load_order(self) -> List[Dict]:
        order = []
        for name, info in sorted(
            self.loaded_modules.items(),
            key=lambda x: x[1].get("priority", 100)
        ):
            order.append({
                "name": name,
                "path": info.get("rel_path", "unknown"),
                "priority": info.get("priority", 100),
                "enabled": info.get("enabled", True)
            })
        return order

    def disable_module(self, module_name: str) -> bool:
        if module_name not in self.loaded_modules:
            return False
        self.loaded_modules[module_name]["enabled"] = False
        self._logger.info(f"🔴 Module '{module_name}' disabled")
        return True

    def enable_module(self, module_name: str) -> bool:
        if module_name not in self.loaded_modules:
            return False
        self.loaded_modules[module_name]["enabled"] = True
        self._logger.info(f"🟢 Module '{module_name}' enabled")
        return True