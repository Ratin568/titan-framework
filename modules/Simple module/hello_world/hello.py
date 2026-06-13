"""
Example of a simple module with a dedicated command
"""
import discord

async def setup_module(bot, event_bus, services):
    print("✅ Hello World module loaded!")
    
    @bot.tree.command(name="hello", description="Say hello")
    async def hello(interaction: discord.Interaction):
        await interaction.response.send_message(f"Hello {interaction.user.mention}! Titan Framework is working!")

    print("   Command /hello registered")