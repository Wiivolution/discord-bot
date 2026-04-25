import discord
import asyncio
from constants import TOKEN
from constants import OWNER_USER_ID
from discord.ext import commands

intents = discord.Intents.all()
allowed_mentions = discord.AllowedMentions(everyone=False, roles=False)

bot = commands.Bot(command_prefix=".", intents=intents, allowed_mentions=allowed_mentions, owner_id=OWNER_USER_ID)

cogs_list = [
    "cogs.extras",
    "cogs.mod"
]

async def load_extensions():
    for cog in cogs_list:
        await bot.load_extension(cog)
        print(f"Successfully loaded {cog}!")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")

async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

asyncio.run(main())