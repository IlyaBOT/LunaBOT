import discord
from core.settings_bot import config
from discord.ext import commands
from discord import app_commands
from core.database import VcDB


class VoiceCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.vc_db = VcDB()

    @app_commands.command(name="vcsetup", description="Created lobby for creating private voices")
    @app_commands.checks.has_permissions(administrator=True)
    async def voice_setup(self, interaction: discord.Interaction):
        if self.vc_db.get_lobby_from_guild(guild_id=interaction.guild.id) is not None:
            print(self.vc_db.get_lobby_from_guild(guild_id=interaction.guild.id))
            return await interaction.response.send_message("You already have a lobby")
        mbed = discord.Embed(
            title="Success!",
            description=f"A lobby has been created on your server to create voice channels ✅",
            color=discord.Color.green()
        )
        vc = await interaction.guild.create_voice_channel(name="[+] Create Voice Channel [+]")
        await interaction.response.send_message(embed=mbed)
        self.vc_db.vc_setup_insert(guild_id=interaction.guild.id, voice_channel_id=vc.id)

    @app_commands.command(name="lock", description="Open access to enter the voice channel for everyone")
    async def voice_lock(self, interaction: discord.Interaction):
        try:
            voice = interaction.user.voice.channel
        except AttributeError:
            return await interaction.response.send_message("You don't have a group created")
        if self.vc_db.get_author_id_vc(channel_id=voice.id) == interaction.user.id:
            overwrite = voice.overwrites_for(interaction.guild.default_role)
            overwrite.connect = False
            await voice.set_permissions(interaction.guild.default_role, overwrite=overwrite)
            await interaction.response.send_message(f"Voice channel `{voice.name}` the locked")
            self.vc_db.update_private_vc(options=False, channel_id=voice.id)
        else:
            await interaction.response.send_message(f"You are not authorized to use this voice room")

    @app_commands.command(name="unlock", description="Close access to enter the voice channel for everyone")
    async def voice_unlock(self, interaction: discord.Interaction):
        try:
            voice = interaction.user.voice.channel
        except AttributeError:
            return await interaction.response.send_message("You don't have a group created")
        if self.vc_db.get_author_id_vc(channel_id=voice.id) == interaction.user.id:
            overwrite = voice.overwrites_for(interaction.guild.default_role)
            overwrite.connect = True
            await voice.set_permissions(interaction.guild.default_role, overwrite=overwrite)
            await interaction.response.send_message(f"Voice channel `{voice.name}` the unlocked")
            self.vc_db.update_private_vc(options=True, channel_id=voice.id)
        else:
            await interaction.response.send_message("You are not authorized to use this voice room")


async def setup(bot: commands.Bot):
    settings = config()
    await bot.add_cog(VoiceCommand(bot), guilds=[discord.Object(id=settings['main_guild'])])
