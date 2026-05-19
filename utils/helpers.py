import discord
import sys
from discord import app_commands
from discord.utils import format_dt
from discord.ext import commands

from constants import BOT_DEVELOPERS
from constants import STAFF_ROLE_ID

from utils.enums import ActionType
from utils.enums import ServerAction

class AppNotBotDeveloper(app_commands.CheckFailure):
    message: str

class AppNotStaffCheck(app_commands.CheckFailure):
    message: str

def get_string_by_action_type(actionType: ActionType):
    match actionType:
        case ActionType.Ban:
            return "Banned"
        case ActionType.Kick:
            return "Kicked"
        case ActionType.Unban:
            return "Unbanned"
        case _:
            return "(Unknown Action Type)"

def get_string_by_server_action(serverAction: ServerAction):
    match serverAction:
        case ServerAction.Join:
            return "Member Joined"
        case ServerAction.Leave:
            return "Member Left"
        case _:
            return "(Unknown Action Type)"

def is_bot_developer():
    async def predicate(interaction: discord.Interaction) -> bool:
        if interaction.user.id in BOT_DEVELOPERS:
            return True
        raise AppNotBotDeveloper("You are not a bot developer, and therefore can't use this command.")
    return app_commands.check(predicate)

def is_staff():
    async def predicate(interaction: discord.Interaction) -> bool:
        user = interaction.user
        role = interaction.guild.get_role(STAFF_ROLE_ID)
        if isinstance(user, discord.Member):
            if role in user.roles:
                return True
        raise AppNotStaffCheck("You are not staff, and therefore can't use this command.")
    return app_commands.check(predicate)

async def check_staff_target(interaction: discord.Interaction, user: discord.User):
    role = interaction.guild.get_role(STAFF_ROLE_ID)
    if isinstance(user, discord.Member):
        if role in user.roles:
            await interaction.response.send_message("You cannot perform this action on this user.", ephemeral=True)
            return True
    return False  

async def post_action_log(interaction: discord.Interaction, target: discord.User, action: ActionType, channel: discord.TextChannel, color: discord.Color, author: discord.User = None, reason: str = None):
    channel = interaction.guild.get_channel(channel)

    embed = discord.Embed(
        title=f"Member {get_string_by_action_type(action)}",
        description=f"Reason: {reason}",
        color=color
    )

    embed.add_field(name="User", value=f"{target.mention} (`{target.name}`) (`{target.id}`)", inline=True) 
    if author is not None:
        embed.add_field(name="Author", value=f"{author.mention} (`{author.name}`) (`{author.id}`)", inline=True)    
    embed.set_thumbnail(url=target.display_avatar.url)

    await channel.send(embeds=[embed])

async def post_server_log(bot: commands.Bot, serverAction: ServerAction, channel: discord.TextChannel, color: discord.Color, target: discord.User = None, note: str = None):
    channel = bot.get_channel(channel)

    embed = discord.Embed(
        title=f"{get_string_by_server_action(serverAction)}",
        description=f"Note: {note}",
        color=color
    )
    
    if target is not None:
        embed.add_field(name="User", value=f"{target.mention} (`{target.name}`) (`{target.id}`)", inline=True) 
        embed.set_thumbnail(url=target.display_avatar.url)

    await channel.send(embeds=[embed])