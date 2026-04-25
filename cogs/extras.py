import discord
import sys
from discord.ext import commands
from discord import app_commands, TextChannel, __version__ as discordpy_version

python_version = sys.version.split()[0]

class Extras(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command(name="sync")
    @commands.is_owner()
    async def sync_app_commands(self, ctx):
        await ctx.bot.tree.sync()
        await ctx.send("Synced app commands successfully!")
    
    @app_commands.command(name="env",  description="Information about the environment the bot is running under")
    async def env_command(self, interaction: discord.Interaction):
        message = f'''
        Python {python_version}\ndiscord.py {discordpy_version}'''
        await interaction.response.send_message(message)

async def setup(bot):
    await bot.add_cog(Extras(bot))