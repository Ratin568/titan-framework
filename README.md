# Titan Framework

<div align="center">

# Titan Framework

### Modular • Event-Driven • Plugin-Based • Zero Restrictions

A modern Discord bot framework built on a **Thin Core Architecture**.

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://python.org)
[![discord.py](https://img.shields.io/badge/discord.py-2.x-5865F2.svg)](https://github.com/Rapptz/discord.py)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/Ratin568/titan-framework?style=social)](https://github.com/Ratin568/titan-framework)
[![GitHub Forks](https://img.shields.io/github/forks/Ratin568/titan-framework?style=social)](https://github.com/Ratin568/titan-framework)
[![GitHub Release](https://img.shields.io/github/v/release/Ratin568/titan-framework)](https://github.com/Ratin568/titan-framework/releases)

**Version:** v2.0.0

Documentation: https://ratin568.github.io/titan-framework/

GitHub: https://github.com/Ratin568/titan-framework

</div>

---

# 🚀 Overview

Titan Framework is a modular, event-driven Discord bot framework designed for developers who need scalability, maintainability, and complete freedom.

The framework follows a Thin Core philosophy: the core provides infrastructure only, while all features live inside independent modules.

## Highlights

- EventBus communication
- Dependency Injection container
- Priority-based module loading
- Runtime hot reload
- JSON configuration
- Built-in AntiSpam system
- Zero restrictions on module capabilities

---

# 📑 Table of Contents

- Features
- Architecture
- Installation
- Quick Start
- Configuration
- Creating Modules
- register.json
- Event System
- Dependency Injection
- Hot Reload
- Comparison
- Troubleshooting
- Contributing
- License

---

# ✨ Features

## 🔌 Plugin-Based Design

Every feature is a module.

Drop a folder into modules/ and Titan can load it.

## ⚡ Event Driven

Modules communicate through events rather than direct references.

## 📦 Dependency Injection

Register services once and use them anywhere.

## 🔄 Hot Reload

Reload modules without restarting the bot.

## 🛡️ AntiSpam

Production-ready moderation tools included.

## 🚫 Zero Restrictions

Modules can do anything Python can do.

---

# ⚡ Quick Start

```bash
git clone https://github.com/Ratin568/titan-framework.git
cd titan-framework
pip install -r requirements.txt
```

Create .env:

```env
DISCORD_TOKEN=YOUR_TOKEN
```

Run:

```bash
python main.py
```

---

# 📦 Installation

Requirements:

| Component | Version |
|------------|-----------|
| Python | 3.11+ |
| discord.py | 2.x |

Install dependencies:

```bash
pip install -r requirements.txt
```
---
# 🔌 Creating a Module

Creating a new module in **Titan Framework** is simple and follows a consistent pattern. Each module is independent and can be added or removed without affecting the core.

---

## 📁 Module Structure

Every module requires two files inside its folder:

```text
modules/your_module/
├── register.json
└── main.py
```

---

## Step 1: Create `register.json`

The `register.json` file tells the framework how to load your module.

```json
{
  "name": "your_module",
  "priority": 50,
  "enabled": true,
  "files": ["main.py"],
  "description": "A brief description of your module",
  "author": "Your Name",
  "version": "1.0.0"
}
```

### Field Descriptions

| Field       | Type    | Required | Description                                 |
| ----------- | ------- | -------- | ------------------------------------------- |
| name        | string  | Yes      | Unique module identifier                    |
| priority    | integer | Yes      | Load order (lower = earlier)                |
| enabled     | boolean | No       | If false, module is ignored (default: true) |
| files       | array   | Yes      | List of Python files to load                |
| description | string  | No       | Short description of your module            |
| author      | string  | No       | Your name or username                       |
| version     | string  | No       | Module version (default: 1.0.0)             |

---

## Step 2: Create `main.py`

The `main.py` file contains your module's logic. The framework looks for a `setup_module` function as the entry point.

```python
from core import *

async def setup_module(bot, event_bus, services):
    """
    This function is called when the module loads.

    Parameters:
    - bot: The Discord bot instance
    - event_bus: EventBus for communication between modules
    - services: ServiceContainer for dependency injection
    """

    print("✅ Your module loaded!")

    # Register a slash command
    @bot.tree.command(name="hello", description="Say hello")
    async def hello(interaction):
        await interaction.response.send_message("Hello from your module!")

    # Listen to an event
    @event_bus.on("message.received")
    async def on_message(event):
        message = event.data.get("message")
        print(f"Message received: {message.content}")

    # Get a service
    logger = services.get("logger")
    logger.info("Module setup complete")
```

---

## Step 3: Register Your Exports

If your module provides services or functions that other modules need to use, you must register them in `config/exports.json`.

This makes them available through:

```python
from core import *
```

### Example `config/exports.json`

```json
{
  "core": [
    "TitanHub",
    "EventBus",
    "Event",
    "ServiceContainer",
    "PriorityRegistry"
  ],
  "modules": {
    "antispam": [
      "is_spamming",
      "get_user_info",
      "punish_user",
      "reset_user",
      "adjust_warnings"
    ],
    "your_module": [
      "hello_handler",
      "get_user_data",
      "format_response"
    ]
  },
  "custom": [
    "MyCustomService",
    "MyCustomClass"
  ]
}
```

### Using Exports From Other Modules

```python
from core import *

async def setup_module(bot, event_bus, services):
    is_spamming = services.get("antispam.is_spamming")

    if is_spamming:
        result = await is_spamming(user_id, message)
```

---

# ⚙️ Configuration System

The framework uses JSON configuration files for all settings.

This keeps your Python code clean and makes it easy to change settings without touching code.

---

## `config/framework.json` – Main Settings

This file contains the core settings for your bot.

```json
{
  "bot": {
    "prefix": "!",
    "guild_id": 1122769174045917265,
    "activity": {
      "name": "Titan System",
      "type": "watching"
    }
  },
  "modules": {
    "search_paths": [
      "modules",
      "plugins",
      "custom_modules"
    ]
  },
  "database": {
    "enabled": false,
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
    "hot_reload": true,
    "auto_sync_commands": true
  }
}
```

### Field Descriptions

| Field                       | Type    | Default        | Description                             |
| --------------------------- | ------- | -------------- | --------------------------------------- |
| bot.prefix                  | string  | `!`            | Command prefix for legacy commands      |
| bot.guild_id                | integer | `null`         | Server ID for faster slash command sync |
| bot.activity.name           | string  | `Titan System` | Status message displayed on Discord     |
| bot.activity.type           | string  | `watching`     | watching, listening, playing, competing |
| modules.search_paths        | array   | `["modules"]`  | Folders to scan for modules             |
| database.enabled            | boolean | `false`        | Enable/disable database connection      |
| database.host               | string  | `localhost`    | Database host address                   |
| database.port               | integer | `3306`         | Database port                           |
| database.user               | string  | `root`         | Database username                       |
| database.password           | string  | `""`           | Database password                       |
| database.name               | string  | `titan_db`     | Database name                           |
| logging.level               | string  | `INFO`         | DEBUG, INFO, WARNING, ERROR, CRITICAL   |
| logging.format              | string  | Custom         | Log format string                       |
| features.hot_reload         | boolean | `true`         | Enable/disable hot reload               |
| features.auto_sync_commands | boolean | `true`         | Auto sync slash commands on startup     |

---

## `config/exports.json` – Export Registry

This file controls what services and functions are available through:

```python
from core import *
```

### Example

```json
{
  "core": [
    "TitanHub",
    "EventBus",
    "Event",
    "ServiceContainer",
    "PriorityRegistry"
  ],
  "modules": {
    "antispam": [
      "is_spamming",
      "get_user_info",
      "punish_user",
      "reset_user",
      "adjust_warnings"
    ],
    "hello_world": []
  },
  "custom": []
}
```

---

## How to Add Your Module's Exports

### Define Functions or Services

```python
# modules/my_module/main.py

from core import *

async def setup_module(bot, event_bus, services):
    services.register(
        "my_module.greeting",
        my_greeting_function
    )

    services.register(
        "my_module.calculator",
        Calculator()
    )

def my_greeting_function(name: str) -> str:
    return f"Hello, {name}!"

class Calculator:
    def add(self, a, b):
        return a + b
```

### Register Them in `exports.json`

```json
{
  "core": [...],
  "modules": {
    "antispam": [...],
    "my_module": [
      "my_greeting_function",
      "Calculator"
    ]
  },
  "custom": []
}
```

### Use Them in Another Module

```python
from core import *

async def setup_module(bot, event_bus, services):

    greeting = services.get("my_module.greeting")
    result = greeting("World")

    calc = services.get("my_module.calculator")
    sum_result = calc.add(5, 3)
```

---

# 🎯 Quick Reference: Export Types

| Export Type     | Where to Register | How Other Modules Access          |
| --------------- | ----------------- | --------------------------------- |
| Core Exports    | `"core"`          | `from core import *`              |
| Module Services | `"modules"`       | `services.get("module.function")` |
| Custom Exports  | `"custom"`        | `from core import *`              |

---

# 💡 Best Practices

* Keep module names unique
* Use descriptive export names
* Document your exports
* Register only what is needed
* Use `ServiceContainer` for shared services
* Avoid exposing internal-only functions
* Keep modules independent and reusable

---

# 🚀 Example: Complete Module

## `modules/logger_module/register.json`

```json
{
  "name": "logger_module",
  "priority": 20,
  "enabled": true,
  "files": ["main.py"],
  "description": "Custom logging service",
  "author": "Your Name",
  "version": "1.0.0"
}
```

---

## `modules/logger_module/main.py`

```python
from core import *

class CustomLogger:

    def __init__(self, name):
        self.name = name

    def log(self, message):
        print(f"[{self.name}] {message}")

async def setup_module(bot, event_bus, services):

    logger = CustomLogger("MyBot")

    services.register(
        "logger_module.instance",
        logger,
        singleton=True
    )

    services.register(
        "logger_module.CustomLogger",
        CustomLogger
    )

    print("✅ Logger module loaded!")

    @bot.tree.command(name="logtest")
    async def log_test(interaction):
        logger.log("Test message from command!")
        await interaction.response.send_message("Logged!")
```

---

## Add to `config/exports.json`

```json
{
  "core": [...],
  "modules": {
    "logger_module": [
      "CustomLogger"
    ]
  },
  "custom": []
}
```

---

## Use in Another Module

```python
from core import *

async def setup_module(bot, event_bus, services):

    logger = services.get(
        "logger_module.instance"
    )

    logger.log(
        "Hello from another module!"
    )

    new_logger = CustomLogger("NewBot")

    new_logger.log(
        "Custom logger created!"
    )
```

---

# 📌 Summary

Titan Framework's export and service architecture allows modules to remain:

* Independent
* Reusable
* Extensible
* Easy to maintain
* Easy to configure

By using `ServiceContainer`, `exports.json`, and the modular loading system, developers can share functionality across modules without modifying the framework core.

**Build once, reuse everywhere. 🚀**

---
---

# 🎯 Event System

Emit:

```python
await event_bus.emit(
    "user_joined",
    user_id=user.id
)
```

Listen:

```python
@event_bus.on("user_joined")
async def handle_join(user_id):
    print(user_id)
```

---

# 🧩 Dependency Injection

Register:

```python
services.register(
    "database",
    Database()
)
```

Use:

```python
db = services.get("database")
```

---

# 🔄 Hot Reload

Benefits:

- Faster development
- Less downtime
- Safer deployments

Workflow:

```text
Edit
 ↓
Reload
 ↓
Updated
```

---


# ⚔️ Titan vs Traditional Frameworks

|  Feature      | Titan  | Traditional |
|---------------|--------|-------------|
| Event Driven      | ✅ | Partial |
| Plugin Based      | ✅ | Partial |
| Hot Reload        | ✅ | Rare    |
| DI Container      | ✅ | Rare    |
| Zero Restrictions | ✅ |   ❌   |

---

# 🔍 Troubleshooting

## Module not loading

Check:

- register.json exists
- enabled = true
- file paths are correct

## Commands missing

```python
await bot.tree.sync()
```

## Service not found

Ensure registration occurs before access.

---

# 🤝 Contributing

1. Fork repository
2. Create branch
3. Commit changes
4. Push changes
5. Open Pull Request

Guidelines:

- Follow PEP 8
- Write documentation
- Keep modules focused
- Add tests when possible

---

# 📚 Documentation

https://ratin568.github.io/titan-framework/

# 🌐 Repository

https://github.com/Ratin568/titan-framework

---

## 📄 License

This project is licensed under the **MIT License** – a permissive open-source license that allows you to do almost anything with the code, as long as you include the original copyright and license notice.

### You are free to:

- ✅ **Use commercially** – In your own products, services, or business
- ✅ **Modify** – Change, adapt, or improve the source code
- ✅ **Distribute** – Share the original or modified version
- ✅ **Create private forks** – For internal or personal use
- ✅ **Build proprietary software** – Use it in closed-source projects

### You must:

- **Keep the original copyright notice** and this license in all copies or substantial portions of the software

### Limitations:

- **THE SOFTWARE IS PROVIDED "AS IS"**, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED
- The author is **NOT LIABLE** for any claim, damages, or other liability arising from the use of the software


The original copyright and license notice must remain included.

---

# 🌟 Philosophy

Strong core.

Unlimited possibilities.

Build Discord bots your way.

---
