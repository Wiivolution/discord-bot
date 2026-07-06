import discord
import sys
from discord import app_commands
from discord.utils import format_dt
from discord.ext import commands

from constants import BOT_DEVELOPERS, MODMAIL_USER_ID, STAFF_ROLE_ID

from utils.enums import ActionType, ServerAction, MessageLog

class AppNotBotDeveloper(app_commands.CheckFailure):
    message: str

class AppNotStaffCheck(app_commands.CheckFailure):
    message: str

class DateOrTimeToSecondsConverter:
    @staticmethod
    def parse(value: str) -> int:
        units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        total_seconds = 0
        
        for token in value.lower().split():
            unit = token[-1]
            if unit not in units:
                raise ValueError("Invalid time unit")
                
            amount = int(token[:-1])
            total_seconds += amount * units[unit]
            
        return total_seconds

class DurationTransformer(app_commands.Transformer):
    async def transform(self, interaction, value: str) -> int:
        return DateOrTimeToSecondsConverter.parse(value)

def get_string_by_action_type(actionType: ActionType) -> str:
    match actionType:
        case ActionType.Ban:
            return "Banned"
        case ActionType.Kick:
            return "Kicked"
        case ActionType.ScamKick:
            return "Scamkicked"
        case ActionType.Unban:
            return "Unbanned"
        case ActionType.Timeout:
            return "Timed Out"
        case ActionType.TimeoutRemoval:
            return "Timeout Removed"
        case _:
            return "(Unknown Action Type)"

def get_string_by_server_action(serverAction: ServerAction) -> str:
    match serverAction:
        case ServerAction.Join:
            return "Member Joined"
        case ServerAction.Leave:
            return "Member Left"
        case _:
            return "(Unknown Action Type)"

def get_string_by_message_log(messageLog: MessageLog) -> str:
    match messageLog:
        case MessageLog.Delete:
            return "Message Deleted"
        case MessageLog.Edit:
            return "Message Edited"
        case _:
            return "(Unknown Action Type)"

def is_bot_developer_app_check():
    async def predicate(interaction: discord.Interaction) -> bool:
        if interaction.user.id in BOT_DEVELOPERS:
            return True
        raise AppNotBotDeveloper("You are not a bot developer, and therefore can't use this command.")
    return app_commands.check(predicate)

def is_staff_app_check():
    async def predicate(interaction: discord.Interaction) -> bool:
        user = interaction.user
        role = interaction.guild.get_role(STAFF_ROLE_ID)
        if isinstance(user, discord.Member):
            if role in user.roles:
                return True
        raise AppNotStaffCheck("You are not staff, and therefore can't use this command.")
    return app_commands.check(predicate)

def is_staff(member: discord.Member, guild: discord.Guild):
    role = guild.get_role(STAFF_ROLE_ID)
    if isinstance(member, discord.Member):
        if role in member.roles:
            return True
    return False

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

async def post_message_log(bot: commands.Bot, messageLog: MessageLog, channel: discord.TextChannel, color: discord.Color, message: discord.Message, new_message: discord.Message = None, note: str = None):
    channel = bot.get_channel(channel)

    embed = discord.Embed(
        title=f"{get_string_by_message_log(messageLog)}",
        description=f"Note: {note}",
        color=color
    )

    author = message.author

    embed.add_field(name="Author", value=f"{author.mention} (`{author.name}`) (`{author.id}`)", inline=False)
    
    if not new_message:
        embed.add_field(name="Message Content", value=f"{message.content}", inline=False)
    else:
        embed.add_field(name="Old Message Content", value=f"{message.content}", inline=True)
        embed.add_field(name="New Message Content", value=f"{new_message.content}", inline=True)
    
    embed.add_field(name="Message Date", value=format_dt(message.created_at), inline=False)

    embed.add_field(name="Message Channel", value=message.channel.mention, inline=True)
    embed.add_field(name="Message Link", value=f"[Jump to message]({message.jump_url})", inline=True)
    embed.add_field(name="Message ID", value=f"`{message.id}`", inline=True)

    await channel.send(embeds=[embed])