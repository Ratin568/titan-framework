import os
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv
import discord
from discord.ext import commands

from core import TitanHub
from core.config_loader import default_config

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# ============================================
# 📥 دریافت تنظیمات از config_loader
# ============================================
PREFIX = default_config.get_prefix()
GUILD_ID = default_config.get_guild_id()
ACTIVITY_NAME = default_config.get("bot.activity.name", "Titan System")
ACTIVITY_TYPE = default_config.get("bot.activity.type", "watching")
LOG_LEVEL = default_config.get("logging.level", "INFO")
LOG_FORMAT = default_config.get("logging.format", "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")

# تنظیمات لاگ
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger("TitanBot")


class TitanBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix=PREFIX, intents=intents, help_command=None, reconnect=True)
        self.hub = None

    async def setup_hook(self):
        logger.info("🚀 Initializing Titan Bot...")

        # مسیرهای جستجو از فایل JSON
        search_paths = [Path(p) for p in default_config.get_modules_paths()]

        self.hub = TitanHub(self, search_paths=search_paths)
        await self.hub.start()

        # همگام‌سازی با Guild ID از فایل JSON
        if GUILD_ID:
            try:
                test_guild = discord.Object(id=GUILD_ID)
                self.tree.copy_global_to(guild=test_guild)
                synced = await self.tree.sync(guild=test_guild)
                logger.info(f"✅ Synced {len(synced)} slash commands")
                for cmd in synced:
                    logger.info(f"   /{cmd.name}")
            except Exception as e:
                logger.error(f"❌ Failed to sync commands: {e}")

    async def on_ready(self):
        logger.info(f"✅ Logged in as {self.user}")
        await self.change_presence(
            activity=discord.Activity(
                type=getattr(discord.ActivityType, ACTIVITY_TYPE.lower()),
                name=ACTIVITY_NAME
            )
        )
        print(f"\n{'='*50}")
        print(f"🤖 Titan Bot is ONLINE!")
        print(f"📡 Logged in as: {self.user}")
        print(f"🔧 Modules loaded: {len(self.hub.registry.loaded_modules)}")
        print(f"{'='*50}\n")


async def main():
    bot = TitanBot()
    try:
        async with bot:
            await bot.start(TOKEN, reconnect=True)
    except KeyboardInterrupt:
        print("🛑 Bot stopped gracefully.")
    except Exception as e:
        print(f"❌ Bot crashed: {e}")
    finally:
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())