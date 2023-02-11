import discord
import logging
from core.database import VcDB
from discord.ext import commands

log = logging.getLogger(f"LunaBot.{__name__}")


class VoiceEvent(commands.Cog):
    def __int__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):

        if after.channel is not None and before.channel is None:
            vc_db = VcDB()
            category = None
            if after.channel.category_id is not None:
                category = discord.utils.get(member.guild.categories, id=after.channel.category_id)

            if vc_db.get_lobby_from_guild(guild_id=member.guild.id) == after.channel.id:
                vc_arg = vc_db.get_argument_voice_from_member_and_guild(member_id=member.id, guild_id=member.guild.id)
                # [0] name channel [1] limit vc [2] private voice
                vc_data = vc_db.get_settings_vc(member_id=member.id, guild_id=member.guild.id)
                if vc_arg is None:
                    log.info("Created new settings")
                    guild = member.guild
                    overwrites = {
                        guild.default_role: discord.PermissionOverwrite(connect=False)
                    }
                    vc = await guild.create_voice_channel(name=f"Voice Lair {member.display_name}",
                                                          category=category, overwrites=overwrites)
                    vc_db.create_vc(vc_id=vc.id,
                                    name=vc.name,
                                    created_at=member.display_name,
                                    created_member_id=member.id,
                                    guild_id=guild.id)
                    await member.move_to(vc)
                elif not vc_arg:
                    log.info("Old settings applied")
                    guild = member.guild

                    if not vc_data[2]:
                        permission = discord.PermissionOverwrite(connect=False)
                    elif vc_data[2]:
                        permission = discord.PermissionOverwrite(connect=True)

                    overwrites = {
                        guild.default_role: permission
                    }
                    vc = await member.guild.create_voice_channel(name=f"{vc_data[0]}",
                                                                 category=category,
                                                                 overwrites=overwrites,
                                                                 user_limit=vc_data[1])
                    vc_db.update_vc_id(id_channel=vc.id, member_id=member.id, guild_id=guild.id)
                    vc_db.argument_voice(disable=True, channel_id=vc.id)

                    await member.move_to(vc)

        elif before.channel is not None and after.channel is None:
            vc_db = VcDB()
            voice_channel = discord.utils.get(member.guild.channels, id=before.channel.id)
            members_count = len(voice_channel.members)
            if members_count == 0:
                vc_arg = vc_db.get_argument_voice(channel_id=before.channel.id)
                if vc_arg:
                    vc_db.argument_voice(disable=False, channel_id=before.channel.id)
                    await voice_channel.delete()


async def setup(bot: commands.Bot):
    await bot.add_cog(VoiceEvent(bot))
