import discord
import asyncio

from discord.ext import commands
from discord.utils import format_dt

from constants import TOKEN
from constants import OWNER_USER_ID
from constants import BOT_ERROR_CHANNEL_ID
from constants import SERVER_LOGS_CHANNEL_ID
from constants import BOT_DEVELOPERS

from utils.enums import ServerAction

from utils.helpers import AppNotBotDeveloper
from utils.helpers import post_server_log

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
async def on_error(event, *args, **kwargs):
    print(f"Error in {event}:")
    import traceback
    traceback.print_exc()

@bot.tree.error
async def on_app_command_error(interaction, error):

    if isinstance(error, AppNotBotDeveloper):
        await interaction.response.send_message(str(error), ephemeral=True)
        return # return so we don't continue for no reason

    channel = bot.get_channel(BOT_ERROR_CHANNEL_ID)

    if channel:
        await channel.send(f"Error in `/{interaction.command.name}`:\n```{error}```")
    if interaction.response.is_done():
        await interaction.followup.send("An error has occured. Please notify Aep of this error immediately.", ephemeral=True)
    else:
        await interaction.response.send_message("An error has occured. Please notify Aep of this error immediately. (apparently interaction didn't finish?)", ephemeral=True)

async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

asyncio.run(main())