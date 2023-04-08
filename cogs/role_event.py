import logging
from discord.ext import commands
from discord import utils
from core.database import RolesDatabase
from asyncio import sleep


class RoleEvent(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.log = logging.getLogger(f"LunaBOT.{__name__}")
        self.role_db = RolesDatabase()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.emoji.id:
            emoji = f"<:{payload.emoji.name}:{payload.emoji.id}>"
        else:
            emoji = payload.emoji.name

        # data - [0] Role Id [1] Channel Id [2] Message post id
        data_db = self.role_db.db_role_get(guild_id=payload.guild_id, emoji=emoji)
        if data_db is None:
            return

        if self.bot.user == payload.user_id:
            return
        if data_db[1] != payload.channel_id:
            return
        if data_db[2] != payload.message_id:
            return

        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        member = message.guild.get_member(payload.user_id)
        try:
            role = utils.get(message.guild.roles, id=data_db[0])
            await member.add_roles(role)
            self.log.info(f"User {member.name} role was given: {role.name}")
        except KeyError as e:
            self.log.error("Key error, role not found for: " + e)
        except AttributeError as e:
            self.log.error(f"Role attribute not found, looks like it is no longer on the server, or has been removed:\n {e}")
            self.log.warning("The settings for this role will be removed from the database.")
            await sleep(10.0)
            _ = self.role_db.db_role_delete(role_id=data_db[0])
            await message.remove_reaction(payload.emoji, member=self.user)
        except Exception as e:
            print(repr(e))

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.emoji.id:
            emoji = f"<:{payload.emoji.name}:{payload.emoji.id}>"
        else:
            emoji = payload.emoji.name

        # data - [0] Role Id [1] Channel Id [2] Message post id
        data_db = self.role_db.db_role_get(guild_id=payload.guild_id, emoji=emoji)
        if data_db is None:
            return

        if self.bot.user.id == payload.user_id:
            return
        if data_db[1] != payload.channel_id:
            return
        if data_db[2] != payload.message_id:
            return

        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        member = message.guild.get_member(payload.user_id)
        try:
            role = utils.get(message.guild.roles, id=data_db[0])
            await member.remove_roles(role)
            self.log.info(f"User {member.name} role has been removed: {role.name}")
        except KeyError as e:
            self.log.error("Key error, role not found for: " + e)
        except AttributeError as e:
            self.log.error(f"Role attribute not found, looks like it is no longer on the server or has been removed\n {e}")
            self.log.warning("The settings for this role will be removed from the database in 10 seconds.")
            await sleep(10.0)
            _ = self.role_db.db_role_delete(role_id=data_db[0])
            await message.clear_reaction(payload.emoji)
        except Exception as e:
            self.log.error(repr(e))


async def setup(bot: commands.Bot):
    await bot.add_cog(RoleEvent(bot))