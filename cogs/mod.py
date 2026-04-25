import discord
import sys
from discord import app_commands
from discord.utils import format_dt
from discord.ext import commands

class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @app_commands.command(name="userinfo", description="Get user info for a specific user")
    @app_commands.default_permissions(ban_members=True)
    @app_commands.guild_only()
    async def user_info_command(self, interaction: discord.Interaction, user: discord.User, ephemeral: bool = False):
        print("begin")
        guild = interaction.guild
        embed = discord.Embed()
        embed.description = (
            f"**User:** {user.mention}\n"
            f"**User's ID:** {user.id}\n"
            f"**Created on:** {format_dt(user.created_at)} ({format_dt(user.created_at, style='R')})\n"
            f"**Default Profile Picture:** {user.default_avatar}\n"
        )
        print("isinstance")
        if isinstance(user, discord.Member):
            member_type = "member"
            embed.description += (
                f"**Join date:** {format_dt(user.joined_at) if user.joined_at else None} ({format_dt(user.joined_at, style='R') if user.joined_at else None})\n"
                f"**Current Status:** {user.status}\n"
                f"**User Activity:** {user.activity}\n"
                f"**Current Display Name:** {user.display_name}\n"
                f"**Nitro Boost Info:** {f'Boosting since {format_dt(user.premium_since)}' if user.premium_since else 'Not a booster'}\n"
                f"**Current Top Role:** {user.top_role}\n"
                f"**Color:** {user.color}\n"
                f"**Profile Picture:** [link]({user.avatar})"
            )
            print("isinstance2")
            if user.guild_avatar:
                embed.description += f"\n**Guild Profile Picture:** [link]({user.guild_avatar})"
            else:
                member_type = "user"
                if guild != None:
                    try:
                        ban = await guild.fetch_ban(user)
                        embed.description += f"\n**Ban reason**: {ban.reason}"
                    except discord.NotFound:
                        pass
        
        embed.title = f"Info for {'bot' if user.bot else 'user'} {user}"
        embed.set_thumbnail(url=user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=ephemeral)

async def setup(bot):
    await bot.add_cog(Mod(bot))