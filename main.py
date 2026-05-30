# general lib imports
import discord
import asyncio
import traceback
import io
from datetime import datetime

from discord.ext import commands
from discord.utils import format_dt

# constants
from constants import TOKEN
from constants import OWNER_USER_ID
from constants import BOT_ERROR_CHANNEL_ID
from constants import SERVER_LOGS_CHANNEL_ID
from constants import MESSAGE_LOGS_CHANNEL_ID
from constants import KILLBOX_CHANNEL_ID
from constants import BOT_DEVELOPERS

# enums
from utils.enums import ServerAction
from utils.enums import MessageLog

# helper functions
from utils.helpers import AppNotBotDeveloper
from utils.helpers import AppNotStaffCheck
from utils.helpers import post_server_log
from utils.helpers import post_message_log

discord.utils.setup_logging()

intents = discord.Intents.all()
allowed_mentions = discord.AllowedMentions(everyone=False, roles=False)

bot = commands.Bot(command_prefix=".", intents=intents, allowed_mentions=allowed_mentions, owner_id=OWNER_USER_ID)

cogs_list = [
    "cogs.extras",
    "cogs.mod",
    "cogs.dev"
]

async def load_extensions():
    for cog in cogs_list:
        await bot.load_extension(cog)
        print(f"Successfully loaded {cog}!")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")

@bot.event
async def on_member_join(member: discord.Member):
    await post_server_log(bot=bot, serverAction=ServerAction.Join, channel=SERVER_LOGS_CHANNEL_ID, color=discord.Color.gold(), target=member, note=f"Created: {member.created_at} ({format_dt(member.created_at)}) ({format_dt(member.created_at, style='R')})")

@bot.event
async def on_member_remove(member: discord.Member):
    await post_server_log(bot=bot, serverAction=ServerAction.Leave, channel=SERVER_LOGS_CHANNEL_ID, color=discord.Color.gold(), target=member, note=f"Created: {member.created_at} ({format_dt(member.created_at)}) ({format_dt(member.created_at, style='R')})")

@bot.event
async def on_message(message: discord.Message):
    if message.channel.id == KILLBOX_CHANNEL_ID:
        print(f"killbox moment {message.author.id}")

    await bot.process_commands(message)

@bot.event
async def on_message_delete(message: discord.Message):
    if isinstance(message.channel, discord.DMChannel):
        return
    if message.author.bot:
        return
    await post_message_log(bot=bot, messageLog=MessageLog.Delete, channel=MESSAGE_LOGS_CHANNEL_ID, color=discord.Color.red(), message=message)

@bot.event
async def on_message_edit(old_message: discord.Message, new_message: discord.Message):
    if isinstance(old_message.channel, discord.DMChannel):
        return
    if old_message.content == new_message.content:
        return
    await post_message_log(bot=bot, messageLog=MessageLog.Edit, channel=MESSAGE_LOGS_CHANNEL_ID, color=discord.Color.blue(), message=old_message, new_message=new_message)

@bot.event
async def on_error(event, *args, **kwargs):
    channel = bot.get_channel(BOT_ERROR_CHANNEL_ID)
    error_text = traceback.format_exc()

    if channel:
        if len(error_text) <= 2000:
            await channel.send(f"Error in {event}\n```py\n{error_text}\n```")
        else:
            file = discord.File(io.BytesIO(error_text.encode("utf-8")), filename=f"{event}_traceback_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt")
            await channel.send(f"Error in {event}", file=file)
            
@bot.tree.error
async def on_app_command_error(interaction, error):
    if isinstance(error, AppNotBotDeveloper) or isinstance(error, AppNotStaffCheck):
        await interaction.response.send_message(str(error), ephemeral=True)
        return # return so we don't continue for no reason

    channel = bot.get_channel(BOT_ERROR_CHANNEL_ID)

    if channel:
        await channel.send(f"Error in `/{interaction.command.qualified_name}`:\n```{error}```") # I should switch to this to an embed, this shit is ugly
    if interaction.response.is_done():
        await interaction.followup.send("An error has occured. Please notify Aep of this error immediately.", ephemeral=True)
    else:
        await interaction.response.send_message("An error has occured. Please notify Aep of this error immediately. (apparently interaction didn't finish?)", ephemeral=True)

async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

asyncio.run(main())