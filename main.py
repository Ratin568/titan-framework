
import os
import asyncio
import logging

from pathlib import Path
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv

import discord
from discord.ext import commands

from core import TitanHub
from core.config_loader import default_config


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")


# ============================================================
# CONFIGURATION
# ============================================================

PREFIX = default_config.get_prefix()
GUILD_ID = default_config.get_guild_id()

ACTIVITY_NAME = default_config.get(
    "bot.activity.name",
    "Titan System"
)

ACTIVITY_TYPE = default_config.get(
    "bot.activity.type",
    "watching"
)

LOG_LEVEL = default_config.get(
    "logging.level",
    "INFO"
)

LOG_FORMAT = default_config.get(
    "logging.format",
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)


# ============================================================
# LOGGING CONFIGURATION
# ============================================================

LOG_DIRECTORY = Path("logs")

LOG_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True
)

console_handler = logging.StreamHandler()

file_handler = RotatingFileHandler(
    LOG_DIRECTORY / "titan_runtime.log",
    maxBytes=5 * 1024 * 1024,
    backupCount=5,
    encoding="utf-8"
)

formatter = logging.Formatter(LOG_FORMAT)

console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

numeric_log_level = getattr(
    logging,
    str(LOG_LEVEL).upper(),
    logging.INFO
)

logging.basicConfig(
    level=numeric_log_level,
    handlers=[
        console_handler,
        file_handler
    ],
    force=True
)

logger = logging.getLogger("TitanBot")


# ============================================================
# TITAN BOT
# ============================================================

class TitanBot(commands.Bot):

    def __init__(self):

        intents = discord.Intents.all()

        super().__init__(
            command_prefix=PREFIX,
            intents=intents,
            help_command=None,
            reconnect=True
        )

        self.hub = None

    # --------------------------------------------------------
    # SETUP HOOK
    # --------------------------------------------------------

    async def setup_hook(self):

        logger.info("🚀 Initializing Titan Bot...")

        # Load module search paths.

        search_paths = [
            Path(path)
            for path in default_config.get_modules_paths()
        ]

        # Initialize Titan Hub.

        self.hub = TitanHub(
            self,
            search_paths=search_paths
        )

        # Load Titan modules.

        await self.hub.start()

        # ----------------------------------------------------
        # SLASH COMMAND SYNCHRONIZATION
        # ----------------------------------------------------

        if GUILD_ID:

            try:

                test_guild = discord.Object(
                    id=GUILD_ID
                )

                self.tree.copy_global_to(
                    guild=test_guild
                )

                synced = await self.tree.sync(
                    guild=test_guild
                )

                logger.info(
                    "✅ Synced %s slash commands",
                    len(synced)
                )

                for command in synced:

                    logger.info(
                        "   /%s",
                        command.name
                    )

            except Exception:

                logger.exception(
                    "❌ Failed to sync commands"
                )

    # --------------------------------------------------------
    # READY EVENT
    # --------------------------------------------------------

    async def on_ready(self):

        logger.info(
            "✅ Logged in as %s",
            self.user
        )

        # Set bot presence.

        try:

            activity_type = getattr(
                discord.ActivityType,
                str(ACTIVITY_TYPE).lower()
            )

            await self.change_presence(
                activity=discord.Activity(
                    type=activity_type,
                    name=ACTIVITY_NAME
                )
            )

        except (AttributeError, ValueError):

            logger.exception(
                "Failed to set bot activity"
            )

        # Startup information.

        loaded_modules = 0

        if self.hub is not None:

            loaded_modules = len(
                self.hub.registry.loaded_modules
            )

        print(f"\n{'=' * 50}")
        print("🤖 Titan Bot is ONLINE!")
        print(f"📡 Logged in as: {self.user}")
        print(f"🔧 Modules loaded: {loaded_modules}")
        print(f"📝 Runtime logs: {LOG_DIRECTORY / 'titan_runtime.log'}")
        print(f"{'=' * 50}\n")


# ============================================================
# MAIN
# ============================================================

async def main():

    if not TOKEN:

        raise RuntimeError(
            "DISCORD_TOKEN was not found. "
            "Check your .env file."
        )

    bot = TitanBot()

    try:

        async with bot:

            await bot.start(
                TOKEN,
                reconnect=True
            )

    except KeyboardInterrupt:

        logger.info(
            "🛑 Bot stopped by user."
        )

    except Exception:

        logger.exception(
            "❌ Titan Bot crashed"
        )

        raise

    finally:

        if not bot.is_closed():

            await bot.close()

        logger.info(
            "Titan Bot shutdown completed."
        )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    try:

        asyncio.run(main())

    except KeyboardInterrupt:

        print("\n🛑 Titan stopped gracefully.")

    except Exception:

        logging.getLogger("TitanBot").exception(
            "Fatal application error"
        )
