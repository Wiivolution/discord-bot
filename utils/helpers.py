import discord
import sys
from discord import app_commands
from discord.utils import format_dt
from discord.ext import commands

from constants import BOT_DEVELOPERS
from constants import STAFF_ROLE_ID

class AppNotBotDeveloper(app_commands.CheckFailure):
    message: str

def is_bot_developer():
    async def predicate(interaction: discord.Interaction) -> bool:
        if interaction.user.id in BOT_DEVELOPERS:
            return True
        raise AppNotBotDeveloper("You are not a bot developer, and therefore can't use this command.")
    return app_commands.check(predicate)

async def check_staff(interaction: discord.Interaction, user: discord.User):
    role = interaction.guild.get_role(STAFF_ROLE_ID)
    if isinstance(user, discord.Member):
        if role in user.roles:
            await interaction.response.send_message("You cannot perform this action on this user.", ephemeral=True)
            return True
    return False