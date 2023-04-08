import discord
import logging
from discord import app_commands
from discord.ext import commands
from core.settings_bot import config
from discord.errors import NotFound
from core.database import RolesDatabase
from core.custom import LangMessageable



class RoleGiver(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.settings = config()
        self.send = LangMessageable.app_mod_send
        self.log = logging.getLogger(f"LunaBOT.{__name__}")
        self.role_db = RolesDatabase()

    @app_commands.command(name="reactroleadd", description="Creates a reaction under a post to get a role.")
    @app_commands.checks.has_permissions(administrator=True)
    async def reactroleadd(self, interaction: discord.Integration, channel: discord.TextChannel, id_message: str, emoji: str,
                role: discord.Role):
        try:
            message = await channel.fetch_message(int(id_message))
            self.role_db.role_insert(guild_id=interaction.guild.id, channel_id=channel.id, message_id=int(id_message), emoji=emoji,
                                role_id=role.id)
            await message.add_reaction(emoji)
            link = "[Message](https://discord.com/channels/{interaction.guild.id}/{channel.id}/{id_message})"
            format_m = (role.mention, emoji, link)
            await self.send(interaction, "✅ `[SUCCESS]` Receiving role: %s\nReaction to get a role: %s and this message %s", format=format_m, ephemeral=True)


        except NotFound as e:
            await self.send(interaction, "💢 [Error] %s", format=(e))


    @app_commands.command(name="reactroleremove", description="Removes the role acquisition reaction.")
    @app_commands.checks.has_permissions(administrator=True)
    async def reactroleremove(self, interaction: discord.Integration, role: discord.Role):
        data = self.role_db.db_role_delete(role_id=role.id)
        if data is None:
            return await self.send(interaction, "⚠ `[Warning]` This role no longer exists or has been removed from the database.")
        channel = self.bot.get_channel(data[1])
        message = await channel.fetch_message(data[0])
        await message.clear_reaction(emoji=data[2])
        await self.send(interaction, "✅ `[SUCCESS]` The issuing role %s was successfully deleted.", format=(role))


async def setup(bot: commands.Bot):
    settings = config()
    await bot.add_cog(RoleGiver(bot), guilds=[discord.Object(id=settings['main_guild'])])