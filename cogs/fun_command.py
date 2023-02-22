import discord
import logging
import random
import datetime
from core.settings_bot import config
from discord.ext import commands
from discord import app_commands


class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.log = logging.getLogger(f"LunaBOT.{__name__}")
        self.config = config()

    @app_commands.command(name="pidortest", description="Тест персоны, использовавшей данную команду на гомосексуальную ориентацию.")
    async def pidortest(self, interaction: discord.Integration, member: discord.Member = None ):
        res = ['gay', 'not gay']
        now = datetime.datetime.now()
        random_result = random.choice(res)
        match random_result:
            case 'gay':
                if member is None:
                    await interaction.response.send_message(f"Внимание, {interaction.user.mention}, Вы пидор❗️", ephemeral=False)
                else:
                    await interaction.response.send_message(f"Внимание, {member.mention},Вы пидор❗️ ", ephemeral=False)
                self.log.info("❗️Внимание, на сервере обнаружен пидор!")
            case 'not gay':
                if member is None:
                    await interaction.response.send_message(f"Поздравляем, {interaction.user.mention}, Вы натурал✅", ephemeral=False)
                else:
                    await interaction.response.send_message(f"Поздравляем, {member.mention}, Вы натурал✅", ephemeral=False)
                
                self.log.info("✅Всё хорошо, просканированный человек оказался натуралом.")


async def setup(bot: commands.Bot):
    settings = config()
    await bot.add_cog(Fun(bot), guilds=[discord.Object(id=settings['main_guild'])])