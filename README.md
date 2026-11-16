# Titan Framework

<div align="center">

# 🧠 Titan Framework

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

- Thin Core (~1500 LOC)
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
- AntiSpam
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

## 🧠 Thin Core

Only essential infrastructure belongs in the core.

## 📦 Dependency Injection

Register services once and use them anywhere.

## 🔄 Hot Reload

Reload modules without restarting the bot.

## 🛡️ AntiSpam

Production-ready moderation tools included.

## 🚫 Zero Restrictions

Modules can do anything Python can do.

---

# 🧠 Thin Core Architecture

Traditional frameworks often become large monoliths.

Titan keeps the core intentionally small.

Core responsibilities:

- Hub
- EventBus
- ServiceContainer
- Registry
- Configuration

Everything else belongs in modules.

Benefits:

- Easier maintenance
- Faster development
- Better scalability
- Cleaner code

---

# 🏗 Project Structure

```text
titan-framework/
├── core/
├── config/
├── modules/
├── docs/
├── main.py
├── requirements.txt
└── README.md
```

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

# ⚙️ Configuration

## framework.json

```json
{
  "prefix": "!",
  "guild_id": 123456789,
  "activity": "Titan Framework",
  "search_paths": ["modules"]
}
```

| Field | Description |
|---------|-------------|
| prefix | Command prefix |
| guild_id | Development guild |
| activity | Bot status |
| search_paths | Module directories |

## exports.json

```json
{
  "core": true,
  "modules": true,
  "custom": true
}
```

---

# 🔌 Creating a Module

## Step 1

Create:

```text
modules/my_module/
```

## Step 2

register.json

```json
{
  "name": "my_module",
  "priority": 50,
  "enabled": true,
  "files": ["main.py"]
}
```

## Step 3

main.py

```python
from core import *

async def setup_module(bot, event_bus, services):

    @bot.tree.command(name="hello")
    async def hello(interaction):
        await interaction.response.send_message(
            "Hello from my module!"
        )
```

---

# 📋 register.json Reference

| Field | Required | Description |
|---------|---------|-------------|
| name | Yes | Module name |
| priority | Yes | Load order |
| enabled | Yes | Enable module |
| files | Yes | Files to load |

Priority examples:

```text
0   Core
10  Database
20  Services
50  Commands
100 Utilities
```

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

# 🛡️ AntiSpam Module

Included features:

- Warning levels
- Decay timers
- Mute roles
- Discord timeout support
- Audit logging

---

# ⚔️ Titan vs Traditional Frameworks

| Feature | Titan | Traditional |
|----------|--------|-------------|
| Thin Core | ✅ | ❌ |
| Event Driven | ✅ | Partial |
| Plugin Based | ✅ | Partial |
| Hot Reload | ✅ | Rare |
| DI Container | ✅ | Rare |
| Zero Restrictions | ✅ | ❌ |

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

# 📜 License

Titan Framework is released under the MIT License.

You may:

- Use commercially
- Modify
- Distribute
- Create private forks
- Build proprietary software

The original copyright and license notice must remain included.

---

# 🌟 Philosophy

Small core.

Unlimited possibilities.

Build Discord bots your way.

---

<div align="center">

### Built with 🧠 by a night architect.

</div>
