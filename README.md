````markdown
# 🦾 Titan Framework

**A modular, event-driven Discord bot framework with priority-based module loading**

Titan is a lightweight yet powerful framework that lets you build Discord bots with hot-reloadable modules, priority-based loading, event-driven architecture, and no limits on what modules can do.

---

## Table of Contents

1. [Features](#features)
2. [Quick Start](#quick-start)
3. [Project Structure](#project-structure)
4. [Understanding Modules](#understanding-modules)
5. [Writing Your First Module (Simple)](#writing-your-first-module-simple)
6. [Writing a Complex Module (AntiSpam Example)](#writing-a-complex-module-antispam-example)
7. [register.json Explained](#registerjson-explained)
8. [Core Architecture](#core-architecture)
9. [Troubleshooting](#troubleshooting)
10. [Contributing](#contributing)
11. [Disclaimer](#disclaimer)
12. [License](#license)

---

## Features

| Feature | Description |
| -------- | ----------- |
| 🔌 Truly Modular | Every feature is a module. Add or remove without touching core |
| ⚡ Priority-Based Loading | Control load order via priority in `register.json` |
| 🎯 Event-Driven | Built-in EventBus for loose coupling between modules |
| 🧩 Service Container | DI-style service sharing between modules |
| 🛡️ Production AntiSpam Module | 700+ line module with warning levels, decay timers, role management |
| 🔄 Hot Reload | Reload modules at runtime without restarting the bot |
| 🚀 No Restrictions | Modules can do **ANYTHING**. No hand-holding, no artificial limits |
| 📦 Zero Boilerplate | Just `register.json` + a Python file |

---

## Quick Start

### Prerequisites

- Python 3.11 or higher
- A Discord Bot Token (Create one at [discord.com/developers/applications](https://discord.com/developers/applications))

### Installation

1. Clone the repository:

```bash
git clone https://github.com/Ratin568/titan-framework.git
cd titan-framework
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment:

```bash
cp .env.example .env
```

4. Edit the `.env` file and move it to the main folder and add your Discord bot token:

```text
DISCORD_TOKEN=your_bot_token_here
```

5. Run the bot:

```bash
python main.py
```

---

## Expected Output

After running, you should see:

- INFO messages showing modules loading
- Priority-based load order
- A message saying **Titan Bot is ONLINE!**
- 6 slash commands synced to Discord

---

## Project Structure

```text
titan-framework/
│
├── core/
│   ├── event_bus.py
│   ├── service_container.py
│   ├── priority_registry.py
│   ├── hub.py
│   └── __init__.py
│
├── modules/
│   ├── antispam/
│   │   ├── register.json
│   │   └── main.py
│   │
│   └── hello_world/
│       ├── register.json
│       └── hello.py
│
├── tests/
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

### Important Notes

- The `core` folder is the heart of the framework. **DO NOT MODIFY** any files inside it.
- All custom code goes inside the `modules` folder.
- Every module must have its own folder.
- Every module must include a `register.json`.
- Every module must contain at least one Python file listed in `register.json`.

---

## Understanding Modules

### What is a Module?

A module is a self-contained feature for your Discord bot.

Examples:

- Spam protection
- Welcome messages
- Music player
- Moderation tools
- Economy system

### Two Types of Modules

| Type | Description | Lines of Code | Example |
| ---- | ----------- | ------------- | -------- |
| Simple Module | Basic functionality | 10-100 | Hello World |
| Complex Module | Advanced functionality | 100+ | AntiSpam |

### Simple Module Example

**What it does:**

- Adds `/hello`
- Replies with `Hello from my module!`

**Why it's simple:**

- No event handlers
- No service registration
- No complex logic

### Complex Module Example

**Features:**

- Spam detection
- Warning levels
- Automatic punishments
- Warning decay
- DM notifications
- Logging
- Admin commands

---

## Writing Your First Module (Simple)

### Step 1

Create:

```text
modules/my_first_module/
```

### Step 2

Create:

```text
register.json
```

### Step 3

Content:

```json
{
  "name": "my_first_module",
  "priority": 50,
  "enabled": true,
  "files": ["main.py"],
  "description": "My first Titan module",
  "author": "Your Name",
  "version": "1.0.0"
}
```

### Step 4

Create:

```text
main.py
```

### Step 5

Content:

```python
async def setup_module(bot, event_bus, services):
    print("✅ My first module loaded!")

    @bot.tree.command(name="hello", description="Say hello")
    async def hello(interaction):
        await interaction.response.send_message(
            "Hello from my module!"
        )
```

### Step 6

Run:

```bash
python main.py
```

---

## Writing a Complex Module (AntiSpam Example)

### File Structure

```text
modules/
└── antispam/
    ├── register.json
    └── main.py
```

### register.json

```json
{
  "name": "antispam",
  "priority": 10,
  "version": "1.0.0",
  "description": "Automatic spam detection and punishment system",
  "author": "Titan Team",
  "enabled": true,
  "files": ["main.py"],
  "exports": [
    "is_spamming",
    "get_user_info",
    "punish_user",
    "reset_user"
  ],
  "requires": []
}
```

### Features

1. Spam detection
2. Warning system
3. Punishment methods
4. User notifications
5. Admin commands
6. Logging

---

## register.json Explained

### Required Fields

| Field | Type | Required |
| ------ | ------ | -------- |
| name | string | YES |
| priority | integer | YES |
| files | array | YES |

### Optional Fields

| Field | Type | Default |
| ------ | ------ | -------- |
| enabled | boolean | true |
| description | string | "" |
| author | string | "" |
| version | string | "1.0.0" |
| exports | array | [] |
| requires | array | [] |

### Example

```json
{
  "name": "my_module",
  "priority": 50,
  "enabled": true,
  "files": ["main.py"],
  "description": "My awesome module"
}
```

---

## Core Architecture

### EventBus

Publish:

```python
await event_bus.publish(
    Event(
        name="event.name",
        source="your_module",
        data={"key": "value"}
    )
)
```

Subscribe:

```python
@event_bus.on("event.name")
async def handle_event(event):
    print(event.data)
```

### ServiceContainer

Register:

```python
services.register(
    "my_service",
    MyClass(),
    singleton=True
)
```

Get service:

```python
my_service = services.get("my_service")
```

### PriorityRegistry

Hot reload:

```python
await hub.registry.reload_module("module_name")
```

---

## Troubleshooting

| Problem | Solution |
| -------- | -------- |
| Module not loading | Check `register.json` |
| Slash commands missing | Wait 1-2 minutes |
| No module named core | Run from project root |
| AntiSpam not working | Check mute role |
| Event handler not called | Verify decorator |
| Priority issue | Lower number loads first |

---

## Contributing

1. Fork the repository
2. Create a branch

```bash
git checkout -b my-module
```

3. Add your module
4. Create `register.json`
5. Write your code
6. Test everything
7. Commit

```bash
git commit -m "Add my amazing module"
```

8. Push

```bash
git push origin my-module
```

9. Open a Pull Request

---

## Disclaimer

**THIS SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.**

The author assumes no responsibility for:

- Data loss
- Policy violations
- Third-party modules
- Misuse of the framework

You are solely responsible for:

- Your use of this software
- Legal compliance
- Your modules
- Your Discord bot

---

## License

```text
MIT License

Copyright (c) 2025 Ratin Keremi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
```
