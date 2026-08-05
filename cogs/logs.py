import discord
from discord import app_commands
from discord.ext import commands

from utils.helpers import post_member_update_log, post_member_role_update
from constants import SERVER_LOGS_CHANNEL_ID

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, old_member: discord.Member, new_member: discord.Member):
        if old_member.accent_color != new_member.accent_color or old_member.accent_colour != new_member.accent_colour:
            await post_member_update_log(channel=self.bot.server_logs_channel, target=old_member, updated_field="Accent Color", old_value=str(old_member.accent_color), new_value=str(new_member.accent_color))
        if old_member.display_icon != new_member.display_icon:
            print("display icon changed")
        # currently no need
        #if old_member.display_name != new_member.display_name:
        #    await post_member_update_log(channel=self.bot.server_logs_channel, target=old_member, updated_field="Nickname", old_value=old_member.display_name, new_value=new_member.display_name)
        #if old_member.pending != new_member.pending:
        #    print("pending status updated")
        #if old_member.guild_avatar != new_member.guild_avatar:
        #    print("guild avatar changed")
        #if old_member.guild_banner != new_member.guild_banner:
        #    print("guild banner changed")
        #if old_member.guild_permissions != new_member.guild_permissions:
        #    print("guild permissions changed")
        if old_member.nick != new_member.nick:
            await post_member_update_log(channel=self.bot.server_logs_channel, target=old_member, updated_field="Nickname", old_value=old_member.display_name, new_value=new_member.display_name)
        if old_member.premium_since != new_member.premium_since:
            await post_member_update_log(channel=self.bot.server_logs_channel, target=old_member, updated_field="Boosting Date", old_value=old_member.premium_since, new_value=new_member.premium_since)
        if old_member.roles != new_member.roles:
            old_roles = {role.id: role for role in old_member.roles}
            new_roles = {role.id: role for role in new_member.roles}
            
            added = [role for role_id, role in new_roles.items() if role_id not in old_roles]
            removed = [role for role_id, role in old_roles.items() if role_id not in new_roles]
            if added:
                updated_value = [role.name for role in added]
                await post_member_role_update(channel=self.bot.server_logs_channel, target=old_member, updated_role=updated_value, added=True)
            if removed:
                updated_value = [role.name for role in removed]
                await post_member_role_update(channel=self.bot.server_logs_channel, target=old_member, updated_role=updated_value, added=False)
        #if old_member.timed_out_until != new_member.timed_out_until:
        #    print("timeout updated")
        #if old_member.top_role != new_member.top_role:
        #    print("top role changed")


async def setup(bot):
    await bot.add_cog(Logs(bot))