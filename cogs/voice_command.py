import discord
import logging
from core.settings_bot import config
from discord.ext import commands
from discord import app_commands
from discord.utils import get
from core.database import VcDB
from core.custom import LangMessageable


class VoiceCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.vc_db = VcDB()
        self.send_app_embed = LangMessageable.app_send_embed
        self.send = LangMessageable.app_mod_send
        self.log = logging.getLogger(f"LunaBOT.{__name__}")

    @app_commands.command(name="vcsetup", description="Created lobby for creating private voices")
    @app_commands.checks.has_permissions(administrator=True)
    async def voice_setup(self, interaction: discord.Interaction):
        if self.vc_db.get_lobby_from_guild(guild_id=interaction.guild.id) is not None:
            return await self.send(interaction, "You already have a lobby", ephemeral=True)
        vc = await interaction.guild.create_voice_channel(name="[+] Create Voice Channel [+]")
        self.vc_db.vc_setup_insert(guild_id=interaction.guild.id, voice_channel_id=vc.id)
        await self.send_app_embed(
            interaction,
            title="Success!",
            description="A lobby has been created on your server to create voice channels ✅",
            color=discord.Color.green()
        )

    @app_commands.command(name="lock", description="Open access to enter the voice channel for everyone")
    async def voice_lock(self, interaction: discord.Interaction):
        try:
            voice = interaction.user.voice.channel
        except AttributeError:
            return await self.send(interaction, "You don't have a group created", ephemeral=True)
        if self.vc_db.get_author_id_vc(channel_id=voice.id) == interaction.user.id:
            overwrite = voice.overwrites_for(interaction.guild.default_role)
            overwrite.connect = False
            await voice.set_permissions(interaction.guild.default_role, overwrite=overwrite)
            await self.send(interaction, "Voice channel `%s` the locked", format=(voice.name), ephemeral=True)
            self.vc_db.update_private_vc(options=False, channel_id=voice.id)
        else:
            await self.send(interaction, "You are not authorized to use this voice room", ephemeral=True)

    @app_commands.command(name="unlock", description="Close access to enter the voice channel for everyone")
    async def voice_unlock(self, interaction: discord.Interaction):
        try:
            voice = interaction.user.voice.channel
        except AttributeError:
            return await self.send(interaction, "You don't have a group created", ephemeral=True)
        if self.vc_db.get_author_id_vc(channel_id=voice.id) == interaction.user.id:
            overwrite = voice.overwrites_for(interaction.guild.default_role)
            overwrite.connect = True
            await voice.set_permissions(interaction.guild.default_role, overwrite=overwrite)
            await self.send(interaction, "Voice channel `%s` the unlocked", format=(voice.name), ephemeral=True)
            self.vc_db.update_private_vc(options=True, channel_id=voice.id)
        else:
            await self.send(interaction, "You are not authorized to use this voice room", ephemeral=True)

    @app_commands.command(name="vcname", description="Change name voice channel")
    async def voice_name(self, interaction: discord.Interaction, name: str):
        try:
            voice = interaction.user.voice.channel
        except AttributeError:
            return await self.send(interaction, "You don't have a group created", ephemeral=True)
        if self.vc_db.get_author_id_vc(channel_id=voice.id) == interaction.user.id:
            await voice.edit(name=name)
            self.vc_db.update_name_vc(name=name, channel_id=voice.id)
            await self.send(interaction, "Name changed: `%s`", format=(name))
        else:
            await self.send(interaction, "You are not authorized to use this voice room", ephemeral=True)

    @app_commands.command(name="setlimit", description="Change limit for voice channel")
    async def voice_limit(self, interaction: discord.Interaction, limit: int):
        try:
            voice = interaction.user.voice.channel
        except AttributeError:
            return await self.send(interaction, "You don't have a group created", ephemeral=True)
        if self.vc_db.get_author_id_vc(channel_id=voice.id) == interaction.user.id:
            await voice.edit(user_limit=limit)
            self.vc_db.update_limit_vc(limit=limit, channel_id=voice.id)
            await self.send(interaction, "Change limit user on: `%s`", format=(limit), ephemeral=True)
        else:
            await self.send(interaction, "You are not authorized to use this voice room", ephemeral=True)

    @app_commands.command(name="vcremove", description="Remove lobby from guild")
    @app_commands.checks.has_permissions(administrator=True)
    async def remove_lobby(self, interaction: discord.Interaction):
        voice = self.vc_db.get_lobby_from_guild(guild_id=interaction.guild.id)
        if voice is not None:
            voice_channel = get(interaction.guild.channels, id=voice)
            await voice_channel.delete()
            self.vc_db.delete_lobby(guild_id=interaction.guild.id)
            await self.send(interaction, "Voice lobby has deleted!", ephemeral=True)
        else:
            await self.send(interaction, "Something went wrong..", ephemeral=True)

    @app_commands.command(name="vcundo", description="Deletes all your saved settings in a private voice channel")
    async def voice_undo(self, interaction: discord.Interaction):
        voice = interaction.user.voice
        if voice is None:
            self.vc_db.delete_vc(member_id=interaction.user.id, guild_id=interaction.guild.id)
            await self.send(interaction, "Settings removed")
        else:
            await self.send(interaction, "You cannot do this when you are in your private voice.", ephemeral=True)

    @app_commands.command(name="vcban", description="Deny access to a private voice channel")
    async def voice_ban(self, interaction: discord.Interaction, member: discord.Member):
        try:
            voice = interaction.user.voice.channel
        except AttributeError:
            return await self.send(interaction, "You don't have a group created", ephemeral=True)
        if self.vc_db.get_author_id_vc(channel_id=voice.id) == interaction.user.id:
            get_user = self.bot.get_user(member.id)
            overwrite = voice.overwrites_for(get_user)
            overwrite.connect = False
            await voice.set_permissions(member, overwrite=overwrite)
            await self.send(interaction, "This voice is closed for this member: `%s`", format=(member.name), ephemeral=True)
        else:
            await self.send(interaction, "You cannot do this when you are in your private voice.", ephemeral=True)

    @app_commands.command(name="vcunban", description="Allow access to private voice channel")
    async def voice_unban(self, interaction: discord.Interaction, member: discord.Member):
        try:
            voice = interaction.user.voice.channel
        except AttributeError:
            return await self.send(interaction, "You don't have a group created", ephemeral=True)
        if self.vc_db.get_author_id_vc(channel_id=voice.id) == interaction.user.id:
            get_user = self.bot.get_user(member.id)
            overwrite = voice.overwrites_for(get_user)
            overwrite.connect = True
            await voice.set_permissions(member, overwrite=overwrite)
            await self.send(interaction, "This voice is open for this member: `%s`", format=(member.name))
        else:
            await self.send(interaction, "You cannot do this when you are in your private voice.", ephemeral=True)


async def setup(bot: commands.Bot):
    settings = config()
    await bot.add_cog(VoiceCommand(bot), guilds=[discord.Object(id=settings['main_guild'])])
