
"""
Titan Logger Demo

Tests the integrated logging system through Discord commands.

Output:
- Console
- Log file
- Discord text channel named "log"
"""

import asyncio
import sys

import discord

from core.logger import BaseHandler, TextFormatter


LOG_CHANNEL_NAME = "log"


class DiscordLogHandler(BaseHandler):
    """Send Titan log records to a Discord text channel."""

    def __init__(self, bot, guild_id=None):
        super().__init__(TextFormatter())
        self.bot = bot
        self.guild_id = guild_id

    def emit(self, record):
        try:
            loop = self.bot.loop

            if loop.is_closed() or not loop.is_running():
                return

            coroutine = self._send(record)

            try:
                running_loop = asyncio.get_running_loop()
            except RuntimeError:
                running_loop = None

            if running_loop is loop:
                loop.create_task(coroutine)
            else:
                asyncio.run_coroutine_threadsafe(coroutine, loop)

        except Exception as error:
            print(
                f"[Titan Discord Logger] {error}",
                file=sys.stderr,
            )

    async def _send(self, record):
        try:
            channel = self._find_channel()

            if channel is None:
                print(
                    f"[Titan Discord Logger] "
                    f"Channel '{LOG_CHANNEL_NAME}' was not found.",
                    file=sys.stderr,
                )
                return

            message = self.formatter.format(record)

            # Prevent accidental mentions.
            message = discord.utils.escape_mentions(message)

            # Avoid breaking Discord code blocks.
            message = message.replace("```", "'''")

            # Discord message limit is 2000 characters.
            if len(message) > 1800:
                message = message[:1800] + "\n... (truncated)"

            await channel.send(
                f"```text\n{message}\n```"
            )

        except Exception as error:
            # Do not send logger errors back through the logger.
            print(
                f"[Titan Discord Logger] Delivery failed: {error}",
                file=sys.stderr,
            )

    def _find_channel(self):
        # Prefer the configured guild.
        if self.guild_id:
            guild = self.bot.get_guild(self.guild_id)

            if guild:
                for channel in guild.text_channels:
                    if channel.name == LOG_CHANNEL_NAME:
                        return channel

        # Fallback: search all available guilds.
        for channel in self.bot.get_all_channels():
            if (
                isinstance(channel, discord.TextChannel)
                and channel.name == LOG_CHANNEL_NAME
            ):
                return channel

        return None


async def setup_module(bot, event_bus, services):
    """Initialize the Logger Demo module."""

    titan = services.get("titan")

    if titan is None:
        raise RuntimeError("Titan service is unavailable")

    # Create a module-specific logger.
    logger = titan.logger.bind(
        module="logger_demo"
    )

    # Attach Discord output to the same Logger Engine.
    discord_handler = DiscordLogHandler(
        bot=bot,
    )

    logger.add_handler(discord_handler)

    # Register the handler for framework access.
    services.register(
        "logger_demo.discord_handler",
        discord_handler,
        singleton=True,
    )

    # Register the module logger.
    services.register(
        "logger_demo.logger",
        logger,
        singleton=True,
    )

    logger.info("Logger Demo module initialized")

    logger.success(
        "Discord logging handler registered",
        destination=LOG_CHANNEL_NAME,
    )

    def run_log_test(user, guild, channel):
        """Generate test records through Titan Logger."""

        context = {
            "user": str(user),
            "user_id": user.id,
            "guild": guild.name if guild else "DM",
            "channel": channel.name,
        }

        logger.info(
            "Logger test command executed",
            **context,
        )

        logger.debug(
            "Debug logging test",
            **context,
        )

        logger.success(
            "Success logging test",
            **context,
        )

        logger.warning(
            "Warning logging test",
            **context,
        )

        logger.audit(
            "LOGGER_TEST_EXECUTED",
            **context,
        )

        logger.error(
            "Error logging test",
            **context,
        )

        try:
            10 / 0

        except ZeroDivisionError as error:
            logger.exception(
                "Exception logging test",
                error,
                **context,
            )

        logger.info(
            "Logger test completed",
            **context,
        )

    # Prefix command: !logtest
    @bot.command(name="logtest")
    async def logtest_prefix(ctx):
        run_log_test(
            user=ctx.author,
            guild=ctx.guild,
            channel=ctx.channel,
        )

        await ctx.reply(
            "Logger test completed. Check the console, log file and #log channel.",
            mention_author=False,
        )

    # Slash command: /logtest
    @bot.tree.command(
        name="logtest",
        description="Test Titan's integrated logging system",
    )
    async def logtest_slash(interaction: discord.Interaction):
        run_log_test(
            user=interaction.user,
            guild=interaction.guild,
            channel=interaction.channel,
        )

        await interaction.response.send_message(
            "Logger test completed. Check the console, log file and #log channel.",
            ephemeral=True,
        )

    logger.success(
        "Logger Demo commands registered",
        commands=["!logtest", "/logtest"],
    )
