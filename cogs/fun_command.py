import discord
import logging
import random
import datetime
from core.settings_bot import config
from discord.ext import commands
from discord import app_commands
from core.custom import LangMessageable


class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.log = logging.getLogger(f"LunaBOT.{__name__}")
        self.send = LangMessageable.app_mod_send
        self.config = config()

    @app_commands.command(name="homotest", description="Test of a person who used a specific command for homosexual orientation.")
    async def pidortest(self, interaction: discord.Integration, member: discord.Member = None ):
        res = ['gay', 'not gay']
        random_result = random.choice(res)
        match random_result:
            case 'gay':
                if member is None:
                    await self.send(interaction, "Warning %s, You pidor ❗️", format=(interaction.user.mention))
                else:
                    await self.send(interaction, "Warning %s, You pidor ❗️", format=(member.mention))
                
                self.log.info("❗️Внимание, на сервере обнаружен пидор!")
            case 'not gay':
                if member is None:
                    await self.send(interaction, "Congratulations %s, you are straight ✅", format=(interaction.user.mention))
                else:
                    await interaction.response.send_message(f"Поздравляем, {member.mention}, Вы натурал✅", ephemeral=False)
                
                self.log.info("✅Всё хорошо, просканированный человек оказался натуралом.")


async def setup(bot: commands.Bot):
    settings = config()
    await bot.add_cog(Fun(bot), guilds=[discord.Object(id=settings['main_guild'])])