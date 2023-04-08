import discord
import logging
from discord.ext import commands
from discord import app_commands
from core.settings_bot import config
from core.settings_bot import CustomChecks
from core.database import GuildSettings
from core.custom import LangMessageable

settings = config()


class LocateSelect(discord.ui.Select):
    def __init__(self, ctx, msg):
        self.guild_settings = GuildSettings()
        options = [
            discord.SelectOption(label="Русский", value="ru_RU", emoji="🇷🇺"),
            discord.SelectOption(label="English", value="en_US", emoji="🇺🇸")
        ]
        self.guild = ctx.guild.id
        self.msg = msg
        self.send_embed = LangMessageable.app_send_embed
        super().__init__(options=options, placeholder="Select to locate", max_values=1)
        
    async def callback(self, interaction: discord.Interaction):
        self.guild_settings.update_lang(guild_id=self.guild, lang=self.values[0])
        if self.values[0] == "ru_RU":
            lang_name = "`Русский` 🇷🇺"
        elif self.values[0] == "en_US":
            lang_name = "`English` 🇺🇸"
        await self.msg.delete()
        await self.send_embed(
            interaction,
            title="✅ SUCCESS",
            description="Language changed to %s",
            format={"description": lang_name},
            color=discord.Colour.green(),
            ephemeral=True
        )

class SelectView(discord.ui.View):
    def __init__(self, *, timeout = 180, ctx, msg):
        super().__init__(timeout=timeout)
        self.add_item(LocateSelect(ctx, msg))
        
    

class ToolsCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.log = logging.getLogger(f"LunaBOT.{__name__}")
        self.send = LangMessageable.mod_send
        self.send_embed = LangMessageable.send_embed

    
    @commands.hybrid_command()
    async def ping(self, ctx):
        await self.send_embed(
            ctx,
            title="Ping!",
            description=f"Pong! 🏓{round(self.bot.latency * 1000)}ms",
            color=discord.Colour.blue()
        )

    @commands.hybrid_command()
    @commands.is_owner()
    @CustomChecks.developer_mode()
    async def reload(self, ctx, extansion):
        try:
            await self.bot.unload_extension(f"cogs.{extansion}")
            await self.bot.load_extension(f"cogs.{extansion}")
            await self.send_embed(
                ctx,
                title="Reload",
                description="Cog `%s` reloaded",
                format={"description": extansion}
            )
            self.log.info(f"Cogs {extansion} reloaded!")
        except commands.errors.ExtensionNotFound:
            await self.send(ctx, "Cog not found.")
            self.log.warning(f"Cogs: {extansion} not found")
        except commands.errors.ExtensionNotLoaded:
            await self.send(ctx, "Cog already loaded.")
            self.log.warning(f"Cogs: {extansion} not reloaded")

    
    @commands.hybrid_command()
    @commands.has_permissions(manage_messages=True)
    async def lang(self, ctx):
       msg = await self.send_embed(
            ctx,
            title="Locate Menus",
            description="Select please lenguage",
        )
       await msg.edit(view=SelectView(ctx=ctx, msg=msg))


async def setup(bot: commands.Bot):
    await bot.add_cog(ToolsCommand(bot), guilds=[discord.Object(id=settings['main_guild'])])