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
| --------- | ----------- |
| 🔌 Truly Modular | Every feature is a module. Add or remove without touching core |
| ⚡ Priority-Based Loading | Control load order via priority in register.json |
| 🎯 Event-Driven | Built-in EventBus for loose coupling between modules |
| 🧩 Service Container | DI-style service sharing between modules |
| 🛡️ Production AntiSpam Module | 700+ line module with warning levels, decay timers, role management |
| 🔄 Hot Reload | Reload modules at runtime without restarting the bot |
| 🚀 No Restrictions | Modules can do ANYTHING. No hand-holding, no artificial limits |
| 📦 Zero Boilerplate | Just register.json + a Python file |

---

## Quick Start

### Prerequisites

- Python 3.11 or higher
- A Discord Bot Token (Create one at discord.com/developers/applications)

### Installation

1. Clone the repository:
   git clone https://github.com/Ratin568/titan-framework.git
   cd titan-framework

2. Install dependencies:
   pip install -r requirements.txt

3. Configure environment:
   cp .env.example .env

4. Edit .env file and add your Discord bot token:
   DISCORD_TOKEN=your_bot_token_here

5. Run the bot:
   python main.py

### Expected Output

After running, you should see:
- INFO messages showing modules loading
- Priority-based load order (antispam first, then hello_world)
- A message saying "Titan Bot is ONLINE!"
- 6 slash commands synced to Discord

---

## Project Structure

The framework has a specific folder structure that you must follow:

titan-framework/
│
├── core/                          # FRAMEWORK CORE - DO NOT MODIFY
│   ├── event_bus.py              # Event-driven communication system
│   ├── service_container.py      # Dependency injection container
│   ├── priority_registry.py      # Module loader with priority system
│   ├── hub.py                    # Central coordinator
│   └── __init__.py               # Core module exports
│
├── modules/                       # ALL MODULES GO HERE
│   │
│   ├── antispam/                 # Example complex module
│   │   ├── register.json         # Module configuration
│   │   └── main.py               # Module code (700+ lines)
│   │
│   └── hello_world/              # Example simple module
│       ├── register.json         # Module configuration
│       └── hello.py              # Module code (minimal)
│
├── tests/                         # Unit tests
├── main.py                        # Entry point (do not modify)
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment template
├── .gitignore                     # Git ignore rules
├── LICENSE                        # MIT License
└── README.md                      # This file

IMPORTANT NOTES:
- The "core" folder is the heart of the framework. DO NOT CHANGE ANY FILES INSIDE IT.
- All your custom code goes inside the "modules" folder.
- Each module MUST have its own folder inside "modules".
- Each module folder MUST contain a register.json file.
- Each module folder MUST contain at least one Python file listed in register.json.

---

## Understanding Modules

### What is a Module?

A module is a self-contained piece of functionality that adds features to your Discord bot. Examples include:
- Spam protection (like AntiSpam)
- Welcome messages
- Music player
- Moderation tools
- Game server status
- Economy system

### Two Types of Modules

| Type | Description | Lines of Code | Example |
|------|-------------|---------------|---------|
| Simple Module | Basic functionality, few commands | 10-100 lines | Hello World |
| Complex Module | Advanced features, multiple systems | 100+ lines | AntiSpam |

### Simple Module Example: Hello World

The Hello World module is the simplest possible module. It demonstrates the bare minimum needed to create a working module.

WHAT IT DOES:
- Adds one slash command: /hello
- When used, replies with "Hello from my module!"

WHY IT'S SIMPLE:
- No event handlers
- No service registration
- No complex logic
- Just one command

WHO SHOULD USE IT:
- Beginners learning the framework
- Testing if the framework works
- Template for creating new modules

### Complex Module Example: AntiSpam

The AntiSpam module is a production-ready spam detection system. It demonstrates advanced framework features.

WHAT IT DOES:
- Detects repeated/similar messages in a time window
- Assigns warning levels (1, 2, or 3) to users
- Applies timeouts or mute roles
- Automatically reduces warning levels after good behavior
- Sends DM notifications to warned users
- Logs all actions to a configured channel
- Provides admin commands for managing warnings

WHY IT'S COMPLEX:
- Uses EventBus to listen for messages
- Registers multiple services for other modules to use
- Manages state (warning counts, timers)
- Implements async timers for decay
- Handles Discord role and timeout APIs
- Over 700 lines of code

HOW IT'S STRUCTURED (within main.py):
1. Constants and configuration at the top
2. Helper functions (apply_punishment, send_dm, get_or_create_role, etc.)
3. Core logic functions (is_spamming, get_user_info)
4. Service registration for other modules
5. Event handler (check_spam) decorated with @event_bus.on
6. Slash command definitions (@bot.tree.command)
7. Cleanup and logging at the end

WHO SHOULD USE IT AS REFERENCE:
- Developers building complex modules
- Anyone needing spam protection
- Learning advanced framework patterns

---

## Writing Your First Module (Simple)

Follow these steps to create a basic "Hello World" module.

### Step 1: Create Module Folder

Inside the "modules" folder, create a new folder. The name should be descriptive and unique.

Example: modules/my_first_module/

### Step 2: Create register.json

Inside your module folder, create a file named "register.json" (exactly this name).

### Step 3: Add register.json Content

{
  "name": "my_first_module",
  "priority": 50,
  "enabled": true,
  "files": ["main.py"],
  "description": "My first Titan module",
  "author": "Your Name",
  "version": "1.0.0"
}

### Step 4: Create main.py

Inside your module folder, create a file named "main.py" (or whatever name you put in the "files" array).

### Step 5: Add main.py Content

async def setup_module(bot, event_bus, services):
    print("✅ My first module loaded!")

    @bot.tree.command(name="hello", description="Say hello")
    async def hello(interaction):
        await interaction.response.send_message(f"Hello from my module!")

### Step 6: Run the Bot

python main.py

The module will load automatically. You should see "✅ My first module loaded!" in the console. In Discord, type /hello and the bot will respond.

---

## Writing a Complex Module (AntiSpam Example)

The AntiSpam module is included as a reference for building complex modules. Here's how it's organized:

### File Structure

modules/antispam/
├── register.json
└── main.py (700+ lines)

### register.json for AntiSpam

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

### Key Features Implemented in AntiSpam

1. SPAM DETECTION LOGIC:
   - Checks message similarity using SequenceMatcher
   - Tracks messages within a time window (default 5 seconds)
   - Counts repeated or similar messages
   - Triggers punishment after threshold (default 10 repeats)

2. WARNING LEVEL SYSTEM:
   - Level 1: 1 minute timeout
   - Level 2: 2 minute timeout
   - Level 3: 5 minute timeout
   - Each level has a decay timer (2, 3, 5 minutes respectively)

3. PUNISHMENT METHODS:
   - Option A: Mute role (creates role if missing)
   - Option B: Discord timeout API

4. USER NOTIFICATIONS:
   - Sends DM when user receives a warning
   - Sends DM when warnings decay
   - Sends DM when warnings are reset

5. ADMIN COMMANDS:
   - /warnings - Check warning status
   - /resetwarnings - Clear all warnings
   - /addwarning - Add one warning
   - /removewarning - Remove one warning
   - /antispamsettings - View current configuration

6. LOGGING:
   - All actions logged to configurable channel
   - Includes user mentions and warning levels

---

## register.json Explained

The register.json file is REQUIRED for every module. It tells the framework how to load your module.

### Required Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | YES | Unique identifier for your module |
| priority | integer | YES | Load order (lower number = loaded earlier) |
| files | array | YES | List of Python files to load |

### Optional Fields

| Field | Type | Default | Description |
|-------|------| --------- | ----------- |
| enabled | boolean | true | If false, module is ignored |
| description | string | "" | Short description of your module |
| author | string | "" | Your name or username |
| version | string | "1.0.0" | Version number of your module |
| exports | array | [] | Service names this module provides |
| requires | array | [] | Module names this module depends on |

### Priority System Explained

The priority number determines WHEN your module loads:

- Lower number = LOADS FIRST
- Higher number = LOADS LAST

PRIORITY EXAMPLES:
- 10: Critical modules (like AntiSpam) - load first
- 50: Normal modules
- 100: Example/Low-priority modules - load last

WHY PRIORITY MATTERS:
- If Module A provides a service that Module B needs, Module A must have lower priority (load first)
- If Module B depends on Module A, put Module A priority lower than Module B

### Example register.json for a Simple Module

{
  "name": "my_module",
  "priority": 50,
  "enabled": true,
  "files": ["main.py"],
  "description": "My awesome module"
}

### Example register.json for a Complex Module with Dependencies

{
  "name": "advanced_mod",
  "priority": 20,
  "enabled": true,
  "files": ["main.py", "helpers.py", "database.py"],
  "description": "Advanced module with multiple files",
  "author": "Your Name",
  "version": "2.0.0",
  "exports": ["advanced_mod.service1", "advanced_mod.service2"],
  "requires": ["antispam", "economy"]
}

---

## Core Architecture

### EventBus

The EventBus is just a pipe - it receives and sends events. It does NO processing, NO queue logic, NO memory.

HOW TO USE:

To publish an event:
await event_bus.publish(Event(
    name="event.name",
    source="your_module",
    data={"key": "value"}
))

To subscribe to events:
@event_bus.on("event.name")
async def handle_event(event):
    print(event.data)

### ServiceContainer

Simple dependency injection container for sharing services between modules.

HOW TO REGISTER A SERVICE:
services.register("my_service", MyClass(), singleton=True)

HOW TO GET A SERVICE:
my_service = services.get("my_service")

SINGLETON vs PROTOTYPE:
- Singleton: Same instance returned every time
- Prototype: New instance created each time

### PriorityRegistry

The module loader that discovers and loads all modules.

WHAT IT DOES:
1. Scans the "modules" folder recursively
2. Finds every register.json file
3. Reads priority values
4. Sorts modules by priority (lowest first)
5. Loads each module in order
6. Calls setup_module for each loaded file
7. Registers any event handlers

HOT RELOAD:
To reload a module without restarting the bot:
await hub.registry.reload_module("module_name")

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Module not loading | Check register.json exists in correct folder and "enabled" is true |
| Slash commands not showing | Wait 1-2 minutes for Discord to register them globally |
| "No module named 'core'" | Run python main.py from project root folder |
| AntiSpam not working | Ensure mute role exists or set USE_MUTE_ROLE = False |
| Event handler not called | Verify @event_bus.on("event.name") decorator is used |
| Priority not respected | Lower number = loads first; check your values |
| Module dependency error | Required module must have lower priority number |

---

## Contributing

1. Fork the repository on GitHub
2. Create a new branch: git checkout -b my-module
3. Add your module to the "modules" folder
4. Create register.json with proper configuration
5. Write your module code in main.py (or multiple files)
6. Test your module thoroughly
7. Commit your changes: git commit -m "Add my amazing module"
8. Push to your fork: git push origin my-module
9. Open a Pull Request on the original repository

MODULE GUIDELINES:
- Each module must have its own folder
- Each module must have register.json
- Use priority numbers between 10 and 100
- Document your module in comments
- Keep modules independent when possible
- Use the "requires" field for dependencies

---

## Disclaimer

THIS SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NONINFRINGEMENT.

IN NO EVENT SHALL THE AUTHOR OR COPYRIGHT HOLDER BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT, OR OTHERWISE, ARISING FROM, OUT OF, OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

THE AUTHOR ASSUMES NO RESPONSIBILITY FOR:
- Any damages or data loss resulting from the use of this software
- Violation of Discord's Terms of Service or any other platform's policies
- Any legal consequences arising from the use of modules created by third parties
- Any misuse of the framework by end users

YOU ARE SOLELY RESPONSIBLE FOR:
- Your use of this software
- Compliance with all applicable laws and regulations
- The behavior of any modules you create or install
- Any actions taken by your Discord bot

This framework is a tool. Like any tool, it can be used for good or bad purposes. The author provides the tool but does not endorse or support any specific use case. Use responsibly.

---

## License

MIT License

Copyright (c) 2025 Ratin Keremi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

Built with concentration by a night architect who turns ideas into systems.