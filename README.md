cat > README.md << 'EOF'
# 🦾 Titan Framework

**A modular, event-driven Discord bot framework with priority-based module loading**

Titan is a lightweight yet powerful framework that lets you build Discord bots with **hot-reloadable modules**, **priority-based loading**, **event-driven architecture**, and **no limits** on what modules can do.

---

## ✨ Features

- 🔌 **Truly Modular** – Every feature is a module. Add or remove without touching core
- ⚡ **Priority-Based Loading** – Control load order via `priority` in `register.json` (lower = higher priority) [citation:10]
- 🎯 **Event-Driven** – Built-in `EventBus` for loose coupling between modules
- 🧩 **Service Container** – DI-style service sharing between modules
- 🛡️ **Production AntiSpam Module** – Warning levels with decay timers, mute role, DMs, logging
- 🚀 **No Restrictions** – Modules can do ANYTHING. No hand-holding, no artificial limits
- 📦 **Zero Boilerplate** – Just `register.json` + a Python file

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/YOUR_USERNAME/titan-framework.git
cd titan-framework
pip install -r requirements.txt
2. Configure
bash
cp .env.example .env
# Edit .env with your Discord bot token
3. Run
bash
python main.py
📦 Writing Your First Module
Step 1: Create folder structure
text
modules/my_first_module/
├── register.json
└── main.py
Step 2: Create register.json
json
{
  "name": "my_first_module",
  "priority": 50,
  "enabled": true,
  "files": ["main.py"]
}
Step 3: Create main.py
python
async def setup_module(bot, event_bus, services):
    print("✅ My first module loaded!")
    
    @bot.tree.command(name="hello", description="Say hello")
    async def hello(interaction):
        await interaction.response.send_message(f"Hello from my module!")
Step 4: Run the bot
The module loads automatically. Use /reload module_name to hot-reload without restart.

📁 Project Structure
text
titan-framework/
├── core/                    # Framework core
│   ├── event_bus.py        # Event-driven communication
│   ├── service_container.py # Dependency injection
│   ├── priority_registry.py # Module loader
│   └── hub.py              # Central coordinator
├── modules/                 # All modules go here
│   ├── antispam/           # Production anti-spam module
│   │   ├── register.json
│   │   └── main.py
│   └── hello_world/        # Minimal example
│       ├── register.json
│       └── hello.py
├── tests/                   # Unit tests
├── main.py
├── requirements.txt
└── README.md
🛡️ Built-in Modules
Module	Priority	Description
antispam	10	Advanced spam detection with warning levels (1-3), decay timers, mute role, DMs
hello_world	100	Minimal example with /hello command
🔧 Core Architecture
EventBus
Just a pipe – receives and sends events

No processing, no queue logic

Both sync and async subscribers

ServiceContainer
Simple DI container

Singleton and prototype support

Factory methods

PriorityRegistry
Recursive module discovery 

Priority-based loading 

Runtime enable/disable

Module reload without restart

🤝 Contributing
Fork the repository

Create your module branch (git checkout -b my-module)

Add your module in modules/ folder

Commit and push

Open a Pull Request

Modules are auto-discovered. No approval needed.

📄 License
MIT – do whatever you want.