import os
import asyncio
import logging
from dotenv import load_dotenv
import discord
from discord.ext import commands

from core.hub import TitanHub

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("BOT_PREFIX", "!")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TitanBot")


class TitanBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix=PREFIX,
            intents=intents,
            help_command=None
        )
        self.hub = None
        self.synced = False  # Prevent duplicate sync
    
    async def setup_hook(self):
        """Before connecting - modules are loaded here"""
        logger.info("Initializing Titan Bot...")
        
        # Hub setup (modules are loaded here and commands are registered)        self.hub = TitanHub(self)
        await self.hub.start()
        
        # Sync commands after loading all modules  
        await self.sync_commands()
    
    async def sync_commands(self):
        """Syncing slash commands with the Discord API"""
        try:
            # To test: sync with a specific guild first (faster than global)
            # Replace the number below with your server ID
            TEST_GUILD_ID = 1122769174045917265  # <-- PUT YOUR SERVER ID HERE
            
            test_guild = discord.Object(id=TEST_GUILD_ID)
            self.tree.copy_global_to(guild=test_guild)
            synced = await self.tree.sync(guild=test_guild)
            
            logger.info(f"✅ Synced {len(synced)} slash commands to test guild")
            for cmd in synced:
                logger.info(f"   /{cmd.name}")
                
        except Exception as e:
            logger.error(f"❌ Failed to sync commands: {e}")
    
    async def on_ready(self):
        logger.info(f"✅ Logged in as {self.user}")
        
        # Bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="Titan System"
            )
        )
        
        print(f"\n{'='*50}")
        print(f"🤖 Titan Bot is ONLINE!")
        print(f"📡 Logged in as: {self.user}")
        print(f"🔧 Modules loaded: {len(self.hub.registry.loaded_modules)}")
        print(f"{'='*50}\n")


async def main():
    bot = TitanBot()
    async with bot:
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())