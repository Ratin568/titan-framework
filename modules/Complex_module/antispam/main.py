"""
AntiSpam Module - Advanced spam detection with warning levels and role-based punishment
"""

import time
import asyncio
from collections import defaultdict
from datetime import datetime, timedelta
from difflib import SequenceMatcher

import discord
from discord.ext import commands
from core import *

# User data storage
user_data = defaultdict(lambda: {
    "last_message": "",
    "last_time": 0,
    "repeat_count": 0,
    "warnings": 0,
    "last_warning_time": 0,
    "timeout_until": 0,
    "is_punished": False,
    "decay_task": None,
    "mute_task": None
})

# ============================================
# SETTINGS - YOU CAN CHANGE THESE
# ============================================

SPAM_TIME_WINDOW = 5                    # Seconds to consider as spam window
SPAM_REPEAT_THRESHOLD = 10              # Number of similar messages to trigger punishment
SIMILARITY_THRESHOLD = 0.7              # 70% similarity required
USE_MUTE_ROLE = True                    # If True: use Mute role, If False: use Discord timeout
MUTE_ROLE_NAME = "Mute"                 # Name of the mute role (only used if USE_MUTE_ROLE = True)

# Warning level settings (timeout in minutes)
# decay_minutes: after this time without new warning, warning decreases
WARNING_LEVELS = {
    0: {"name": "No Warn", "timeout_minutes": 1, "role_name": None, "decay_minutes": 2},
    1: {"name": "Warn 1", "timeout_minutes": 1, "role_name": "Warn 1", "decay_minutes": 2},
    2: {"name": "Warn 2", "timeout_minutes": 2, "role_name": "Warn 2", "decay_minutes": 3},
    3: {"name": "Warn 3", "timeout_minutes": 5, "role_name": "Warn 3", "decay_minutes": 5}
}

# Log channel ID (set this to your channel ID)
LOG_CHANNEL_ID = None

# ============================================


async def setup_module(bot, event_bus, services):
    print("[AntiSpam] Starting up...")
    print(f"[AntiSpam] Mute method: {'Mute Role' if USE_MUTE_ROLE else 'Discord Timeout'}")

    async def get_or_create_mute_role(guild: discord.Guild) -> discord.Role:
        """Get or create the Mute role"""
        if not USE_MUTE_ROLE:
            return None
        
        role = discord.utils.get(guild.roles, name=MUTE_ROLE_NAME)
        if not role:
            try:
                role = await guild.create_role(
                    name=MUTE_ROLE_NAME,
                    permissions=discord.Permissions.none(),
                    reason="AntiSpam system - Mute role"
                )
                # Deny permissions in all text channels
                for channel in guild.text_channels:
                    try:
                        await channel.set_permissions(role, send_messages=False, add_reactions=False)
                    except:
                        pass
                # Deny permissions in all voice channels
                for channel in guild.voice_channels:
                    try:
                        await channel.set_permissions(role, speak=False, connect=False)
                    except:
                        pass
                print(f"[AntiSpam] Created Mute role: {role.name}")
            except Exception as e:
                print(f"[AntiSpam] Failed to create Mute role: {e}")
        return role

    async def apply_punishment(member: discord.Member, duration_minutes: int, reason: str = "spamming"):
        """Apply mute punishment (either role or Discord timeout)"""
        if USE_MUTE_ROLE:
            # Use Mute role
            mute_role = await get_or_create_mute_role(member.guild)
            if mute_role:
                try:
                    if mute_role not in member.roles:
                        await member.add_roles(mute_role, reason=reason)
                        print(f"[AntiSpam] Applied Mute role to {member}")
                except Exception as e:
                    print(f"[AntiSpam] Failed to apply Mute role: {e}")
                    return
                
                # Schedule role removal
                async def remove_mute_role_after_delay():
                    await asyncio.sleep(duration_minutes * 60)
                    try:
                        if mute_role in member.roles:
                            await member.remove_roles(mute_role, reason="Timeout expired")
                            print(f"[AntiSpam] Removed Mute role from {member}")
                    except Exception as e:
                        print(f"[AntiSpam] Failed to remove Mute role: {e}")
                
                task = asyncio.create_task(remove_mute_role_after_delay())
                user_data[member.id]["mute_task"] = task
        else:
            # Use Discord timeout
            try:
                await member.timeout(duration=timedelta(minutes=duration_minutes), reason=reason)
                print(f"[AntiSpam] Applied Discord timeout to {member} for {duration_minutes} minutes")
            except Exception as e:
                print(f"[AntiSpam] Failed to apply Discord timeout: {e}")

    async def remove_punishment(member: discord.Member):
        """Remove mute punishment (either role or Discord timeout)"""
        if USE_MUTE_ROLE:
            mute_role = discord.utils.get(member.guild.roles, name=MUTE_ROLE_NAME)
            if mute_role and mute_role in member.roles:
                try:
                    await member.remove_roles(mute_role, reason="Punishment ended")
                    print(f"[AntiSpam] Removed Mute role from {member}")
                except Exception as e:
                    print(f"[AntiSpam] Failed to remove Mute role: {e}")
        else:
            try:
                await member.timeout(duration=None)
                print(f"[AntiSpam] Removed Discord timeout from {member}")
            except Exception as e:
                print(f"[AntiSpam] Failed to remove Discord timeout: {e}")

    async def send_log(guild_id: int, embed: discord.Embed):
        """Send log to configured log channel"""
        if not LOG_CHANNEL_ID:
            return
        channel = bot.get_channel(LOG_CHANNEL_ID)
        if channel:
            try:
                await channel.send(embed=embed)
            except Exception as e:
                print(f"[AntiSpam] Failed to send log: {e}")

    async def send_dm(member: discord.Member, title: str, description: str, color: discord.Color):
        """Send DM to user"""
        try:
            embed = discord.Embed(
                title=title,
                description=description,
                color=color,
                timestamp=datetime.utcnow()
            )
            await member.send(embed=embed)
        except:
            pass

    async def get_or_create_role(guild: discord.Guild, role_name: str) -> discord.Role:
        """Get or create a role by name"""
        role = discord.utils.get(guild.roles, name=role_name)
        if not role:
            try:
                role = await guild.create_role(
                    name=role_name,
                    reason="AntiSpam system - Auto created"
                )
                print(f"[AntiSpam] Created role: {role_name}")
            except Exception as e:
                print(f"[AntiSpam] Failed to create role {role_name}: {e}")
        return role

    async def apply_warning_role(member: discord.Member, warning_level: int):
        """Apply warning role based on warning level (does NOT affect chat permissions)"""
        if warning_level < 1 or warning_level > 3:
            return
        
        role_info = WARNING_LEVELS[warning_level]
        if not role_info["role_name"]:
            return
        
        role = await get_or_create_role(member.guild, role_info["role_name"])
        if role:
            try:
                # Remove lower warning roles
                for level in range(1, warning_level):
                    lower_role_info = WARNING_LEVELS[level]
                    if lower_role_info["role_name"]:
                        lower_role = discord.utils.get(member.guild.roles, name=lower_role_info["role_name"])
                        if lower_role and lower_role in member.roles:
                            await member.remove_roles(lower_role)
                
                # Add current warning role
                if role not in member.roles:
                    await member.add_roles(role)
                    print(f"[AntiSpam] Applied role {role.name} to {member}")
            except Exception as e:
                print(f"[AntiSpam] Failed to apply role: {e}")

    async def clear_warning_roles(member: discord.Member):
        """Remove all warning roles from member"""
        for level in range(1, 4):
            role_info = WARNING_LEVELS[level]
            if role_info["role_name"]:
                role = discord.utils.get(member.guild.roles, name=role_info["role_name"])
                if role and role in member.roles:
                    try:
                        await member.remove_roles(role)
                        print(f"[AntiSpam] Removed role {role.name} from {member}")
                    except Exception as e:
                        print(f"[AntiSpam] Failed to remove role: {e}")

    async def start_decay_timer(user_id: int, member: discord.Member, current_warnings: int):
        """Start a timer to decay warnings after specified time"""
        user = user_data[user_id]
        
        # Cancel existing decay task if any
        if user["decay_task"] and not user["decay_task"].done():
            user["decay_task"].cancel()
        
        decay_minutes = WARNING_LEVELS[current_warnings]["decay_minutes"]
        
        async def decay_after_delay():
            await asyncio.sleep(decay_minutes * 60)
            
            # Check if warnings haven't changed during this time
            current = user_data[user_id]["warnings"]
            if current == current_warnings:
                # Decay the warning
                new_warnings = current_warnings - 1
                user_data[user_id]["warnings"] = new_warnings
                
                if new_warnings == 0:
                    # Fully cleared
                    user_data[user_id]["is_punished"] = False
                    user_data[user_id]["repeat_count"] = 0
                    user_data[user_id]["last_message"] = ""
                    user_data[user_id]["timeout_until"] = 0
                    
                    await clear_warning_roles(member)
                    
                    print(f"[AntiSpam] Warnings fully cleared for {member}")
                    
                    # Send DM
                    await send_dm(
                        member,
                        "✅ Your Warnings Have Been Cleared",
                        f"Your warnings in **{member.guild.name}** have been cleared due to good behavior!",
                        discord.Color.green()
                    )
                    
                    # Send log
                    log_embed = discord.Embed(
                        title="✅ Warnings Cleared",
                        description=f"**User:** {member.mention}\nAll warnings have been cleared due to good behavior",
                        color=discord.Color.green(),
                        timestamp=datetime.utcnow()
                    )
                    await send_log(member.guild.id, log_embed)
                else:
                    # Downgrade warning role
                    user_data[user_id]["is_punished"] = True
                    await apply_warning_role(member, new_warnings)
                    print(f"[AntiSpam] Warning decayed from {current_warnings} to {new_warnings} for {member}")
                    
                    # Send DM
                    await send_dm(
                        member,
                        "⚠️ Your Warning Level Has Decreased",
                        f"Your warning level in **{member.guild.name}** has decreased from {current_warnings}/3 to {new_warnings}/3!",
                        discord.Color.green()
                    )
                    
                    # Send log
                    log_embed = discord.Embed(
                        title="🛡️ Warning Decayed",
                        description=f"**User:** {member.mention}\nWarning level decreased from {current_warnings}/3 to {new_warnings}/3",
                        color=discord.Color.green(),
                        timestamp=datetime.utcnow()
                    )
                    await send_log(member.guild.id, log_embed)
                    
                    # Start next decay timer if still has warnings
                    if new_warnings > 0:
                        await start_decay_timer(user_id, member, new_warnings)
        
        task = asyncio.create_task(decay_after_delay())
        user["decay_task"] = task

    def is_similar(text1: str, text2: str) -> bool:
        if text1 == text2:
            return True
        text1 = text1.lower().strip()
        text2 = text2.lower().strip()
        if not text1 or not text2:
            return False
        ratio = SequenceMatcher(None, text1, text2).ratio()
        return ratio >= SIMILARITY_THRESHOLD

    def is_spamming(user_id: int, message_content: str) -> bool:
        user = user_data[user_id]
        if user["is_punished"]:
            return False
        
        now = time.time()
        if user["timeout_until"] > now:
            return True
        
        if (is_similar(user["last_message"], message_content) and 
            (now - user["last_time"]) < SPAM_TIME_WINDOW):
            user["repeat_count"] += 1
            user["last_time"] = now
        else:
            user["last_message"] = message_content
            user["last_time"] = now
            user["repeat_count"] = 1
        
        if user["repeat_count"] >= SPAM_REPEAT_THRESHOLD:
            user["repeat_count"] = 0
            return True
        
        return False

    def get_user_info(user_id: int) -> dict:
        user = user_data[user_id]
        now = time.time()
        return {
            "warnings": user["warnings"],
            "is_timeouted": user["timeout_until"] > now,
            "timeout_remaining": max(0, user["timeout_until"] - now)
        }

    async def punish_user(member: discord.Member, message_channel, reason: str = "spamming"):
        user = user_data[member.id]
        current_warnings = user["warnings"]
        
        if user["is_punished"]:
            return
        
        # Determine next warning level
        if current_warnings == 0:
            new_warnings = 1
        elif current_warnings == 1:
            new_warnings = 2
        elif current_warnings == 2:
            new_warnings = 3
        else:
            new_warnings = 3
        
        # Update user data
        user["warnings"] = new_warnings
        user["last_warning_time"] = time.time()
        user["repeat_count"] = 0
        user["last_message"] = ""
        user["is_punished"] = True
        
        timeout_minutes = WARNING_LEVELS[new_warnings]["timeout_minutes"]
        timeout_seconds = timeout_minutes * 60
        user["timeout_until"] = time.time() + timeout_seconds
        
        # Apply warning role (does NOT affect chat)
        await apply_warning_role(member, new_warnings)
        
        # Apply mute punishment (either role or Discord timeout)
        await apply_punishment(member, timeout_minutes, reason)
        
        # Start decay timer for this warning level
        await start_decay_timer(member.id, member, new_warnings)
        
        # Prepare duration text
        if timeout_minutes >= 1440:
            duration_text = f"{timeout_minutes // 1440} days"
        elif timeout_minutes >= 60:
            duration_text = f"{timeout_minutes // 60} hours"
        else:
            duration_text = f"{timeout_minutes} minutes"
        
        # Send embed to channel (ONLY ONCE when punished)
        embed = discord.Embed(
            title="🛡️ Anti-Spam Protection",
            description=f"{member.mention} has been muted for **{duration_text}** due to {reason}",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Warning Level", value=f"**{new_warnings}/3**", inline=True)
        await message_channel.send(embed=embed)
        
        # Send DM to user
        await send_dm(
            member,
            "🛡️ You Have Been Warned",
            f"You have received a warning in **{member.guild.name}** for {reason}\n\n"
            f"**Warning Level:** {new_warnings}/3\n"
            f"**Mute Duration:** {duration_text}\n\n"
            f"*Your warning will automatically decrease if you behave well.*",
            discord.Color.red()
        )
        
        # Send log
        log_embed = discord.Embed(
            title="🛡️ User Warned",
            description=f"**User:** {member.mention}\n**Reason:** {reason}\n**Warning Level:** {new_warnings}/3\n**Duration:** {duration_text}",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        await send_log(member.guild.id, log_embed)
        
        print(f"[AntiSpam] {member} punished - Warning level {new_warnings}")

    async def reset_user_warnings(member: discord.Member, reset_by: discord.Member = None):
        user = user_data[member.id]
        old_warnings = user["warnings"]
        
        # Cancel existing tasks
        if user["decay_task"] and not user["decay_task"].done():
            user["decay_task"].cancel()
        if user["mute_task"] and not user["mute_task"].done():
            user["mute_task"].cancel()
        
        user["warnings"] = 0
        user["repeat_count"] = 0
        user["last_message"] = ""
        user["last_warning_time"] = 0
        user["timeout_until"] = 0
        user["is_punished"] = False
        user["decay_task"] = None
        user["mute_task"] = None
        
        # Remove punishment
        await remove_punishment(member)
        
        # Remove warning roles
        await clear_warning_roles(member)
        
        # Send DM to user
        await send_dm(
            member,
            "✅ Your Warnings Have Been Reset",
            f"An administrator has reset your warnings in **{member.guild.name}**.\n"
            f"You now have **0/3** warnings.",
            discord.Color.green()
        )
        
        # Send log
        log_embed = discord.Embed(
            title="✅ Warnings Reset",
            description=f"**User:** {member.mention}\n**Previous Warnings:** {old_warnings}/3\n**Reset by:** {reset_by.mention if reset_by else 'System'}",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        await send_log(member.guild.id, log_embed)
        print(f"[AntiSpam] Warnings reset for {member}")

    async def adjust_warnings(member: discord.Member, delta: int, adjust_by: discord.Member):
        user = user_data[member.id]
        old_warnings = user["warnings"]
        
        new_warnings = max(0, min(3, old_warnings + delta))
        
        if new_warnings == old_warnings:
            return
        
        # Cancel existing decay task
        if user["decay_task"] and not user["decay_task"].done():
            user["decay_task"].cancel()
        
        user["warnings"] = new_warnings
        user["last_warning_time"] = time.time()
        
        if new_warnings == 0:
            user["is_punished"] = False
            user["timeout_until"] = 0
            await clear_warning_roles(member)
            await remove_punishment(member)
            
            # Send DM
            await send_dm(
                member,
                "✅ Your Warnings Have Been Cleared",
                f"An administrator has cleared your warnings in **{member.guild.name}**.",
                discord.Color.green()
            )
        else:
            user["is_punished"] = True
            await apply_warning_role(member, new_warnings)
            timeout_minutes = WARNING_LEVELS[new_warnings]["timeout_minutes"]
            user["timeout_until"] = time.time() + (timeout_minutes * 60)
            await apply_punishment(member, timeout_minutes, "Warning adjustment")
            await start_decay_timer(member.id, member, new_warnings)
            
            # Send DM
            timeout_minutes = WARNING_LEVELS[new_warnings]["timeout_minutes"]
            if timeout_minutes >= 1440:
                duration_text = f"{timeout_minutes // 1440} days"
            elif timeout_minutes >= 60:
                duration_text = f"{timeout_minutes // 60} hours"
            else:
                duration_text = f"{timeout_minutes} minutes"
            
            await send_dm(
                member,
                "⚠️ Your Warning Level Has Changed",
                f"An administrator has changed your warning level in **{member.guild.name}**.\n\n"
                f"**New Level:** {new_warnings}/3\n"
                f"Mute Duration: {duration_text}",
                discord.Color.orange()
            )
        
        action = "Increased" if delta > 0 else "Decreased"
        log_embed = discord.Embed(
            title=f"🛡️ Warnings {action}",
            description=f"**User:** {member.mention}\n**Old Level:** {old_warnings}/3\n**New Level:** {new_warnings}/3\n**Adjusted by:** {adjust_by.mention}",
            color=discord.Color.orange(),
            timestamp=datetime.utcnow()
        )
        await send_log(member.guild.id, log_embed)
        print(f"[AntiSpam] Warnings {action.lower()} for {member}: {old_warnings} -> {new_warnings}")

    # Register services
    services.register("antispam.is_spamming", is_spamming)
    services.register("antispam.get_user_info", get_user_info)
    services.register("antispam.punish_user", punish_user)
    services.register("antispam.reset_user", reset_user_warnings)
    services.register("antispam.adjust_warnings", adjust_warnings)
    
    print("[AntiSpam] Services registered")

    @event_bus.on("message.received")
    async def check_spam(event):
        message = event.data.get("message")
        if not message or message.author.bot:
            return
        
        user = user_data[message.author.id]
        
        # Only check for spam if user is not currently punished
        if not user["is_punished"]:
            if is_spamming(message.author.id, message.content):
                await punish_user(message.author, message.channel, "spamming")
                try:
                    await message.delete()
                except:
                    pass

    # Slash Commands
    @bot.tree.command(name="warnings", description="Show warning info for a user")
    async def show_warnings(interaction: discord.Interaction, member: discord.Member = None):
        target = member or interaction.user
        info = get_user_info(target.id)
        
        if info["is_timeouted"]:
            remaining_minutes = int(info["timeout_remaining"] / 60)
            if remaining_minutes >= 1440:
                remaining_text = f"{remaining_minutes // 1440} days"
            elif remaining_minutes >= 60:
                remaining_text = f"{remaining_minutes // 60} hours"
            else:
                remaining_text = f"{remaining_minutes} minutes"
            status = f"⏳ Muted ({remaining_text} left)"
        else:
            status = "✅ Active"
        
        embed = discord.Embed(
            title=f"🛡️ {target.display_name}'s Warnings",
            color=discord.Color.orange() if info["warnings"] > 0 else discord.Color.green()
        )
        embed.add_field(name="Warning Level", value=f"{info['warnings']}/3", inline=True)
        embed.add_field(name="Status", value=status, inline=True)
        
        if info["warnings"] > 0:
            decay_minutes = WARNING_LEVELS[info["warnings"]]["decay_minutes"]
            embed.set_footer(text=f"Warning will decay after {decay_minutes} minutes of good behavior")
        
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="resetwarnings", description="Reset all warnings for a user (Admin only)")
    async def reset_warnings_cmd(interaction: discord.Interaction, member: discord.Member):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Admin only!", ephemeral=True)
            return
        
        await reset_user_warnings(member, interaction.user)
        embed = discord.Embed(
            title="✅ Warnings Reset",
            description=f"All warnings for {member.mention} have been cleared. DM sent to user.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="addwarning", description="Add one warning to a user (Admin only)")
    async def add_warning(interaction: discord.Interaction, member: discord.Member):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Admin only!", ephemeral=True)
            return
        
        info = get_user_info(member.id)
        if info["warnings"] >= 3:
            await interaction.response.send_message(f"❌ {member.mention} already at maximum (3/3)", ephemeral=True)
            return
        
        await adjust_warnings(member, 1, interaction.user)
        embed = discord.Embed(
            title="⚠️ Warning Added",
            description=f"Added 1 warning to {member.mention}\nNew level: {info['warnings'] + 1}/3\nDM sent to user.",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="removewarning", description="Remove one warning from a user (Admin only)")
    async def remove_warning(interaction: discord.Interaction, member: discord.Member):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Admin only!", ephemeral=True)
            return
        
        info = get_user_info(member.id)
        if info["warnings"] == 0:
            await interaction.response.send_message(f"❌ {member.mention} has no warnings", ephemeral=True)
            return
        
        await adjust_warnings(member, -1, interaction.user)
        embed = discord.Embed(
            title="✅ Warning Removed",
            description=f"Removed 1 warning from {member.mention}\nNew level: {info['warnings'] - 1}/3\nDM sent to user.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="antispamsettings", description="Show anti-spam settings (Admin only)")
    async def show_settings(interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Admin only!", ephemeral=True)
            return
        
        embed = discord.Embed(title="🛡️ Anti-Spam Settings", color=discord.Color.blue())
        embed.add_field(name="Time Window", value=f"{SPAM_TIME_WINDOW} seconds", inline=True)
        embed.add_field(name="Repeat Threshold", value=f"{SPAM_REPEAT_THRESHOLD} times", inline=True)
        embed.add_field(name="Similarity Threshold", value=f"{int(SIMILARITY_THRESHOLD * 100)}%", inline=True)
        embed.add_field(name="Mute Method", value=f"{'Mute Role (' + MUTE_ROLE_NAME + ')' if USE_MUTE_ROLE else 'Discord Timeout'}", inline=True)
        
        for level in range(1, 4):
            info = WARNING_LEVELS[level]
            minutes = info["timeout_minutes"]
            if minutes >= 1440:
                duration = f"{minutes // 1440} days"
            elif minutes >= 60:
                duration = f"{minutes // 60} hours"
            else:
                duration = f"{minutes} minutes"
            embed.add_field(name=f"Warn {level}", value=f"Role: `{info['role_name']}`\nMute: {duration}\nDecay: {info['decay_minutes']} minutes", inline=True)
        
        await interaction.response.send_message(embed=embed)

    @bot.event
    async def on_message(message):
        event = Event(name="message.received", source="discord", data={"message": message})
        await event_bus.publish(event)
        await bot.process_commands(message)

    await event_bus.publish(Event(name="module.ready", source="antispam", data={"message": "AntiSpam system is ready"}))
    
    print("[AntiSpam] Module ready!")
    print("   /warnings [user] - Show warnings")
    print("   /resetwarnings <user> - Reset all warnings (admin)")
    print("   /addwarning <user> - Add warning (admin)")
    print("   /removewarning <user> - Remove warning (admin)")
    print("   /antispamsettings - Show settings (admin)")