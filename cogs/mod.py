import discord
from discord import app_commands
from discord.utils import format_dt
from discord.ext import commands

import sys

from utils.helpers import check_staff_target, is_staff, post_action_log
from utils.enums import ActionType

from constants import MODMAIL_USER_ID, DISCORD_OAUTH2_LINK, DISCORD_USER_URL, MOD_LOGS_CHANNEL_ID

class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @app_commands.default_permissions(manage_messages=True)
    @app_commands.guild_only()
    @app_commands.describe(amount="The amount of messages to purge", channel="The channel to purge messages in, if not the current one")
    @app_commands.command(name="purge", description="Purge a certain amount of the latest messages from a channel. Pinned messages are ignored.")
    async def purge_command(self, interaction: discord.Interaction, amount: int, channel: discord.TextChannel = None):
        await interaction.response.defer(ephemeral=True)
        if channel == None:
            channel = interaction.channel
        
        if not channel.permissions_for(interaction.user).manage_messages:
            await interaction.followup.send("You do not have the Manage Messages permission in this channel, and therefore can't use this.", ephemeral=True)
            return

        checks = [lambda m: not m.pinned]

        def check(message):
            return all(c(message) for c in checks)

        try:
            deleted = await channel.purge(limit=amount,
                                          check=check, reason=f"Purged by {interaction.user}")
        except discord.HTTPException as exc:
            return await interaction.followup.send(f"Deleting messages failed {exc}", ephemeral=True)
        if deleted:
            # eventually log here something.
            await interaction.followup.send(f"Successfully deleted {len(deleted)} messages in {channel.mention}!")
        else:
            await interaction.followup.send("No messages were deleted.", ephemeral=True)\
        
    # todo: switch to an embed, or hell rewrite user-info
    @app_commands.guild_only()
    @app_commands.command(name="user-info", description="Get user info for a specific user")
    async def user_info_command(self, interaction: discord.Interaction, user: discord.User = None, ephemeral: bool = False):
        if user == None: # why not
            user = interaction.user
        if not is_staff(member=interaction.user, guild=interaction.guild) and user.id != interaction.user.id:
            await interaction.response.send_message("This commmand can only be used on yourself.", ephemeral=True)
            return
        guild = interaction.guild
        embed = discord.Embed()
        embed.description = (
            f"**User:** {user.mention}\n"
            f"**User's ID:** `{user.id}`\n"
            f"**Created on:** {format_dt(user.created_at)} ({format_dt(user.created_at, style='R')})\n"
            f"**Default Profile Picture:** {user.default_avatar}\n"
        )
        if isinstance(user, discord.Member):
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
            if user.guild_avatar:
                embed.description += f"\n**Guild Profile Picture:** [link]({user.guild_avatar})"

        if guild != None:
            try:
                ban = await guild.fetch_ban(user)
                embed.description += f"\n**Ban reason**: {ban.reason}"
            except discord.NotFound:
                pass
        
        embed.title = f"Info for {'bot' if user.bot else 'user'} {user}"
        embed.set_thumbnail(url=user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=ephemeral)

    @app_commands.default_permissions(kick_members=True)
    @app_commands.guild_only()
    @app_commands.describe(user="The user to kick", reason="Reason for the kick", silent="Opt out of notifying the user of the kick via DM")
    @app_commands.command(name="kick", description="Kick a user, and send them a direct message with a reason")
    async def kick_user_command(self, interaction: discord.Interaction, user: discord.Member, reason: str = None, silent: bool = False): # a kick needs them to be in the server, so we use discord.Member instead of discord.User
        if await check_staff_target(interaction, user):
            return
        
        if not isinstance(user, discord.Member):
            await interaction.response.send_message(f"{user.mention} ({user.id}) is not in the server!", ephemeral=True)
            return
        
        if not silent:
            information_embed = discord.Embed(
                title=f"You were kicked from {interaction.guild.name}.",
                description=f"Reason: {reason}\n\nYou are able to rejoin the server, however please make sure to read the rules before participating again.",
                color=discord.Color.red()
            )

            try:
                await user.send(embeds=[information_embed])
            except discord.Forbidden:
                pass # user disabled dms or left
        
        try:
            await interaction.guild.kick(user, reason=reason)
        except discord.errors.Forbidden as forbidden_to_kick_exception:
            await interaction.response.send_message(f"Failed to kick member: {forbidden_to_kick_exception}", ephemeral=True)
            return
        
        await interaction.response.send_message(f"{user} is now gone.")
        await post_action_log(interaction=interaction, author=interaction.user, target=user, action=ActionType.Kick, channel=MOD_LOGS_CHANNEL_ID, reason=reason, color=discord.Color.red())

    @app_commands.default_permissions(ban_members=True)
    @app_commands.guild_only()
    @app_commands.describe(user="The user to ban", reason="Reason for the ban", remove_messages="Number of days of messages to delete (up to 7 max)", silent="Opt out of notifying the user of the ban via DM")
    @app_commands.command(name="ban", description="Ban a user, and send them a direct message with a reason")
    async def ban_user_command(self, interaction: discord.Interaction, user: discord.User, reason: str = None, remove_messages: app_commands.Range[int, 0, 7] = 0, silent: bool = False):
        if await check_staff_target(interaction, user):
            return

        if isinstance(user, discord.Member) and not silent:
            information_embed = discord.Embed(
                title=f"You were banned from {interaction.guild.name}.",
                description=f"Reason: {reason}",
                color=discord.Color.red()
            )

            appeals_embed = discord.Embed(
                title=f"Appeal Information",
                description=f"You may appeal your ban by DMing <@{MODMAIL_USER_ID}>. You will have to add it to your Authorized Apps, which you can do by clicking Add App on it, or using [this url]({DISCORD_OAUTH2_LINK}{MODMAIL_USER_ID}). If this shows up as unknown-user, try using this user URL in your browser: {DISCORD_USER_URL}{MODMAIL_USER_ID}.",
                color=discord.Color.dark_red()
            )

            try:
                await user.send(embeds=[information_embed, appeals_embed])
            except discord.Forbidden:
                pass # user disabled dms or left
        
        try:
            await interaction.guild.ban(user, reason=reason, delete_message_days=remove_messages)
        except discord.errors.Forbidden as forbidden_to_ban_exception:
            await interaction.response.send_message(f"Failed to ban member: {forbidden_to_ban_exception}", ephemeral=True)
            return
        
        await interaction.response.send_message(f"{user} is now banned.")
        await post_action_log(interaction=interaction, author=interaction.user, target=user, action=ActionType.Ban, channel=MOD_LOGS_CHANNEL_ID, reason=reason, color=discord.Color.red())

    @app_commands.default_permissions(ban_members=True)
    @app_commands.guild_only()
    @app_commands.describe(user="The user to unban", reason="Reason to unban the user")
    @app_commands.command(name="unban", description="Unban a user")
    async def unban_user_command(self, interaction: discord.Interaction, user: discord.User, reason: str = None):
        try:
            await interaction.guild.fetch_ban(user)
        except discord.errors.NotFound:
            return await interaction.response.send_message(f"{user} ({user.id}) is not banned!", ephemeral=True)
        
        try:
            await interaction.guild.unban(user, reason=reason)
        except discord.errors.Forbidden as forbidden_to_unban_exception:
            await interaction.response.send_message(f"Failed to unban member: {forbidden_to_unban_exception}", ephemeral=True)
            return

        await interaction.response.send_message(f"{user} is now unbanned.")
        await post_action_log(interaction=interaction, author=interaction.user, target=user, action=ActionType.Unban, channel=MOD_LOGS_CHANNEL_ID, reason=reason, color=discord.Color(0xFFFFFF))

async def setup(bot):
    await bot.add_cog(Mod(bot))
