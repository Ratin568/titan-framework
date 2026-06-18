"""
Config Loader - Load JSON configs
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List


class ConfigLoader:
    """Loading and managing JSON configurations"""

    def __init__(self, config_dir: Optional[Path] = None):
        if config_dir is None:
            config_dir = Path("config")

        self.config_dir = config_dir
        self.framework_config: Dict[str, Any] = {}
        self.exports_config: Dict[str, Any] = {}

        self._load_framework_config()
        self._load_exports_config()

    def _load_framework_config(self):
        """Loading framework.json"""
        path = self.config_dir / "framework.json"
        if not path.exists():
            self.framework_config = self._get_default_framework_config()
            self._save_json(path, self.framework_config)
        else:
            with open(path, "r", encoding="utf-8") as f:
                self.framework_config = json.load(f)

    def _load_exports_config(self):
        """Load exports.json"""
        path = self.config_dir / "exports.json"
        if not path.exists():
            self.exports_config = self._get_default_exports_config()
            self._save_json(path, self.exports_config)
        else:
            with open(path, "r", encoding="utf-8") as f:
                self.exports_config = json.load(f)

    def _get_default_framework_config(self) -> Dict[str, Any]:
        """Default Framework Configuration"""
        return {
            "$schema": "https://titan-framework.com/schema/framework.json",
            "version": "2.0.0",
            "bot": {
                "prefix": "!",
                "guild_id": None,
                "activity": {"name": "Titan System", "type": "watching"}
            },
            "modules": {
                "search_paths": ["modules", "plugins", "custom_modules"]
            },
            "database": {
                "enabled": False,
                "host": "localhost",
                "port": 3306,
                "user": "root",
                "password": "",
                "name": "titan_db"
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
            },
            "features": {
                "hot_reload": True,
                "auto_sync_commands": True
            }
        }

    def _get_default_exports_config(self) -> Dict[str, Any]:
        """Default Export Configuration"""
        return {
            "$schema": "https://titan-framework.com/schema/exports.json",
            "version": "2.0.0",
            "core": [
                "TitanHub",
                "EventBus",
                "Event",
                "ServiceContainer",
                "PriorityRegistry"
            ],
            "modules": {},
            "custom": []
        }

    def _save_json(self, path: Path, data: Dict[str, Any]):
        """Save JSON file"""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # ===== Config access methods =====

    def get_framework_config(self) -> Dict[str, Any]:
        return self.framework_config

    def get_exports_config(self) -> Dict[str, Any]:
        return self.exports_config

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from framework.json with dot notation"""
        keys = key.split(".")
        value = self.framework_config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def get_bot_config(self) -> Dict[str, Any]:
        return self.framework_config.get("bot", {})

    def get_modules_paths(self) -> List[str]:
        return self.framework_config.get("modules", {}).get("search_paths", ["modules"])

    def get_database_config(self) -> Dict[str, Any]:
        return self.framework_config.get("database", {})

    def get_logging_config(self) -> Dict[str, Any]:
        return self.framework_config.get("logging", {})

    def get_features_config(self) -> Dict[str, Any]:
        return self.framework_config.get("features", {})

    def get_prefix(self) -> str:
        return self.get("bot.prefix", "!")

    def get_guild_id(self) -> Optional[int]:
        guild_id = self.get("bot.guild_id")
        if guild_id:
            return int(guild_id)
        return None

    def get_exports(self) -> List[str]:
        """Get the full list of exports from exports.json"""
        exports = []
        exports.extend(self.exports_config.get("core", []))
        for module_exports in self.exports_config.get("modules", {}).values():
            exports.extend(module_exports)
        exports.extend(self.exports_config.get("custom", []))
        return exports

    def get_core_exports(self) -> List[str]:
        return self.exports_config.get("core", [])

    def get_module_exports(self, module_name: str) -> List[str]:
        return self.exports_config.get("modules", {}).get(module_name, [])

    def get_custom_exports(self) -> List[str]:
        return self.exports_config.get("custom", [])

    def add_custom_export(self, export_name: str):
        """Add new Export to custom list"""
        if export_name not in self.exports_config.get("custom", []):
            self.exports_config.setdefault("custom", []).append(export_name)
            self._save_json(self.config_dir / "exports.json", self.exports_config)


# Default example for quick use
default_config = ConfigLoader()