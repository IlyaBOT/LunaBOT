import discord
import logging
from discord.ext import commands
from discord import app_commands
from core.settings_bot import config
from core.settings_bot import CustomChecks

settings = config()


class ToolsCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.log = logging.getLogger(f"LunaBOT.{__name__}")

    @commands.hybrid_command(name="ping", with_app_command=True)
    @app_commands.guilds(discord.Object(id=settings['main_guild']))
    async def ping(self, ctx):
        await ctx.send(f"Pong! 🏓{round(self.bot.latency * 1000)}ms")

    @commands.command()
    @commands.is_owner()
    @CustomChecks.developer_mode()
    async def reload(self, ctx, extansion):
        try:
            await self.bot.unload_extension(f"cogs.{extansion}")
            await self.bot.load_extension(f"cogs.{extansion}")
            await ctx.reply(f"Cog `{extansion}` reloaded")
            self.log.info(f"Cogs {extansion} reloaded!")
        except commands.errors.ExtensionNotFound:
            await ctx.reply("Cog not found.")
            self.log.warning(f"Cogs: {extansion} not found")
        except commands.errors.ExtensionNotLoaded:
            await ctx.reply("Cog already loaded.")
            self.log.warning(f"Cogs: {extansion} not reloaded")


async def setup(bot: commands.Bot):
    await bot.add_cog(ToolsCommand(bot), guilds=[discord.Object(id=settings['main_guild'])])