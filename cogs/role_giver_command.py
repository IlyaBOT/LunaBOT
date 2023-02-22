import discord
import logging
from discord import app_commands
from discord.ext import commands
from core.settings_bot import config
from discord.errors import NotFound
from core.database import RolesDatabase


class RoleGiver(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.settings = config()
        self.log = logging.getLogger(f"LunaBOT.{__name__}")
        self.role_db = RolesDatabase()

    @app_commands.command(name="reactroleadd", description="Создаёт реакцию под сообщением для получения роли.")
    @app_commands.checks.has_permissions(administrator=True)
    async def reactroleadd(self, interaction: discord.Integration, channel: discord.TextChannel, id_message: str, emoji: str,
                role: discord.Role):
        try:
            message = await channel.fetch_message(int(id_message))
            self.role_db.role_insert(guild_id=interaction.guild.id, channel_id=channel.id, message_id=int(id_message), emoji=emoji,
                                role_id=role.id)
            await message.add_reaction(emoji)
            await interaction.response.send_message(
                f"✅ `[УСПЕХ]` Получаемая роль: {role.mention}\n"
                f"Реакция для получения роли: {emoji}"
                f" на этом сообщении [Message](https://discord.com/channels/{interaction.guild.id}/{channel.id}/{id_message})",
                ephemeral=True)
        except NotFound as e:
            await interaction.response.send_message(f"💢 [ОШИБКА] {e}", ephemeral=True)

    @app_commands.command(name="reactroleremove", description="Удаляет реакцию на получение роли.")
    @app_commands.checks.has_permissions(administrator=True)
    async def reactroleremove(self, interaction: discord.Integration, role: discord.Role):
        data = self.role_db.db_role_delete(role_id=role.id)
        if data is None:
            await interaction.response.send_message("⚠ `[Внимание]` Эта роль большне не существует или уже удалена из базы данных.", ephemeral=True)
            return
        channel = self.bot.get_channel(data[1])
        message = await channel.fetch_message(data[0])
        await message.clear_reaction(emoji=data[2])
        await interaction.response.send_message(f"✅ `[УСПЕХ]` Роль выдачи {role.mention} была успешно удалена.", ephemeral=True)


async def setup(bot: commands.Bot):
    settings = config()
    await bot.add_cog(RoleGiver(bot), guilds=[discord.Object(id=settings['main_guild'])])