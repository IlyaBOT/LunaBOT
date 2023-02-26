import logging

import discord
from discord import app_commands, Interaction
from discord.ext import commands
from discord.ext.commands import errors
from core.settings_bot import NotDeveloperMode, AppNotIsNsfw


class ErrorHandlerApp(commands.Cog):
    def __init__(self, bot: commands.Bot):
        ...
        # assign the handler
        bot.tree.on_error = self.global_app_command_error
        self.log = logging.getLogger(f"LunaBOT.{__name__}")

    async def global_app_command_error(
            self,
            interaction: Interaction,
            error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.MissingPermissions):
            self.log.info("Missing Permissions")
            await interaction.response.send_message("You do not have permission to use this command")

        elif isinstance(error, AppNotIsNsfw):
            self.log.info(f"{error}")
            embed_error = discord.Embed(
                title="Channel not NSFW",
                description=f"{error}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed_error, ephemeral=True)
        else:
            # disclaimer: this is an example implementation.
            self.log.error("An error occurred in the following command:", interaction.command, exc_info=error)


class ErrorHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.log = logging.getLogger(f"LunaBOT.{__name__}")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, err):
        if isinstance(err, errors.MissingRequiredArgument):
            await ctx.send_help(ctx.command)
        elif isinstance(err, errors.NotOwner):
            self.log.warning(f"{err}")
        elif isinstance(err, NotDeveloperMode):
            self.log.warning("To use these commands, enable the developer mode in the bot config")
        else:
            self.log.critical(f"Error LunaBot: {err}", exc_info=err)


async def setup(bot: commands.Bot):
    await bot.add_cog(ErrorHandlerApp(bot))
    await bot.add_cog(ErrorHandler(bot))
