import discord
import sys
from discord import app_commands
from discord.utils import format_dt
from discord.ext import commands

from utils.helpers import is_bot_developer

class Dev(commands.GroupCog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @app_commands.command(name="bot-username", description="Set bot username")
    @is_bot_developer()
    async def set_bot_username_command(self, interaction: discord.Interaction, new_username: str):
        await interaction.response.defer(ephemeral=True)
        await self.bot.user.edit(username=new_username)
        await interaction.followup.send(f"Successfully updated bot username to {new_username}!")

    @app_commands.command(name="bot-avatar", description="Set bot avatar")
    @is_bot_developer()
    async def set_bot_avatar(self, interaction: discord.Interaction, file: discord.Attachment):
        if not file.content_type or file.content_type not in (
            "image/jpeg",
            "image/png",
            "image/gif",
        ):
            return await interaction.response.send_message(
                "File provided is not a valid image.", ephemeral=True
            )

        image_bytes = await file.read()
        try:
            await self.bot.user.edit(avatar=image_bytes)
        except ValueError:
            await interaction.response.send_message(
                "The image has a invalid format.", ephemeral=True
            )
        except discord.HTTPException as exc:
            embed = create_error_embed(interaction, exc)
            await interaction.response.send_message(
                "Failure to edit the bot's profile.",
                embed=embed,
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "Profile picture changed successfully.", ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(Dev(bot))