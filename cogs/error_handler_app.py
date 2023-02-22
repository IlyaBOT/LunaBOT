import logging
from discord import app_commands, Interaction
from discord.ext import commands


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
        else:
            # disclaimer: this is an example implementation.
            self.log.error("An error occurred in the following command:", interaction.command, exc_info=error)


async def setup(bot: commands.Bot):
    await bot.add_cog(ErrorHandlerApp(bot))