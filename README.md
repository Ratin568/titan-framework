# 🦾 Titan Framework

<p align="center">
  <strong>A modular, event-driven Discord bot framework for building scalable bots.</strong>
</p>

<p align="center">
  Hot Reload • Priority-Based Loading • Event Bus • Service Container • Zero Boilerplate
</p>

---

## ✨ Features

- 🔌 **Fully Modular** – Every feature lives in its own module.
- ⚡ **Priority-Based Loader** – Control startup order with `register.json`.
- 🎯 **Event-Driven Architecture** – Loose coupling through EventBus.
- 🧩 **Service Container** – Share services between modules.
- 🔄 **Hot Reload** – Reload modules without restarting the bot.
- 🛡️ **Production-Ready AntiSpam** – Advanced warning and punishment system.
- 🚀 **Minimal Boilerplate** – Create a module with just a JSON file and Python code.

---

## 📚 Table of Contents

- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Modules](#-modules)
- [Creating a Module](#-creating-a-module)
- [register.json](#-registerjson)
- [Core Components](#-core-components)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🚀 Quick Start

### Requirements

- Python 3.11+
- Discord Bot Token

### Installation

```bash
git clone https://github.com/Ratin568/titan-framework.git
cd titan-framework
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:

```text
DISCORD_TOKEN=your_bot_token_here
```

Run:

```bash
python main.py
```

---

## 📂 Project Structure

```text
titan-framework/
├── core/
├── modules/
│   ├── antispam/
│   └── hello_world/
├── tests/
├── main.py
├── requirements.txt
└── README.md
```

> **Note**
>
> Never modify the `core` directory. All custom features belong inside `modules`.

---

## 🧩 Modules

A module is an isolated feature that can be loaded independently.

Examples:

- AntiSpam
- Welcome System
- Music Player
- Economy
- Moderation Tools

### Simple Module

- Small amount of code
- One or two commands
- No complex dependencies

### Complex Module

- Multiple services
- Event listeners
- Internal state management
- Advanced Discord integrations

---

## 🛠 Creating a Module

Create:

```text
modules/my_module/
```

Create `register.json`:

```json
{
  "name": "my_module",
  "priority": 50,
  "enabled": true,
  "files": ["main.py"]
}
```

Create `main.py`:

```python
async def setup_module(bot, event_bus, services):
    @bot.tree.command(
        name="hello",
        description="Say hello"
    )
    async def hello(interaction):
        await interaction.response.send_message(
            "Hello from my module!"
        )
```

---

## 📄 register.json

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| name | string | Unique module identifier |
| priority | integer | Load order |
| files | array | Python files to load |

### Optional Fields

| Field | Default |
|-------|----------|
| enabled | true |
| description | "" |
| author | "" |
| version | "1.0.0" |
| exports | [] |
| requires | [] |

---

## ⚙ Core Components

### EventBus

```python
await event_bus.publish(
    Event(
        name="event.name",
        source="module",
        data={}
    )
)
```

### ServiceContainer

```python
services.register(
    "service",
    MyService(),
    singleton=True
)
```

### Hot Reload

```python
await hub.registry.reload_module(
    "module_name"
)
```

---

## 🧯 Troubleshooting

| Problem | Solution |
|----------|-----------|
| Module not loading | Check `register.json` |
| Slash commands missing | Wait for Discord sync |
| Import errors | Run from project root |
| Event not firing | Verify decorator |
| Priority issue | Lower number loads first |

---

## 🤝 Contributing

1. Fork the repository
2. Create a branch
3. Build your module
4. Test it
5. Submit a Pull Request

---

## ⚠ Disclaimer

This project is provided **AS IS** without warranty of any kind.

You are responsible for:

- Your bot
- Your modules
- Compliance with platform rules
- Legal use of the framework

---

## 📜 License

MIT License

---

<p align="center">
Built with concentration by a night architect who turns ideas into systems.
</p>
