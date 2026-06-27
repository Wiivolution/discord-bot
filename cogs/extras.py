import discord
import sys
from discord.ext import commands
from discord import app_commands, TextChannel

from utils.helpers import is_staff

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

    @commands.command(name="testcommand")
    async def test_prefix_command(self, ctx):
        await ctx.send("Prefix commands work!")

    @app_commands.guild_only()
    @app_commands.describe(channel="The channel to send the message in, if not the current channge", message="The message to send")
    @app_commands.command(name="speak", description="Send a message as the bot")
    @is_staff()
    async def speak_command(self, interaction: discord.Interaction, message: str, channel: discord.TextChannel = None):
        if channel == None:
            channel = interaction.channel
        await channel.send(message)
        await interaction.response.send_message(f"Message sent to channel {channel.mention}!", ephemeral=True) # ideal to respond to the interaction or else we might have issues

async def setup(bot):
    await bot.add_cog(Extras(bot))