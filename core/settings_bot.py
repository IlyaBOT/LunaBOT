import json
import discord
from discord.ext import commands
from discord import app_commands


def config(filename: str = 'appsettings'):
    try:
        with open(f"{filename}.json", "r", encoding='utf-8') as settings:
            return json.load(settings)
    except FileNotFoundError as e:
        print("[ERROR] JSON configuration file was not found")
        exit()


class NotDeveloperMode(commands.CheckFailure):
    pass


class AppNotIsNsfw(app_commands.AppCommandError):
    pass


class CustomChecks:
    @staticmethod
    def developer_mode():
        settings = config()

        async def predicate(ctx):
            if settings['developer_mode'] is False:
                raise NotDeveloperMode("To use these commands, enable the developer mode in the bot config")
            return True

        return commands.check(predicate)

    @staticmethod
    def app_is_nsfw(interaction: discord.Interaction):
        channel = interaction.guild.get_channel(interaction.channel.id)
        if channel.is_nsfw() is False:
            raise AppNotIsNsfw("This is a non-NSFW channel, you cannot use this command here")
        return True
