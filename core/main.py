import discord
import logging
from random import choice
from discord.ext import commands, tasks
from core.database import init_bot_db, RolesDatabase, GuildSettings
from core.settings_bot import config


role_db = RolesDatabase()
settings = config()


class DiscordClient(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        self.log = logging.getLogger(f"LunaBOT.{__name__}")
        self.guild_settings = GuildSettings()
        super().__init__(
            command_prefix=settings['prefix'],
            owner_id=settings['is_owner'],
            intents=intents)

    async def setup_bot(self): 
        init_bot_db()
        if not self.guild_settings.get_all_guild():
            for guild in self.guilds:
                self.guild_settings.setup_guild(guild_id=guild.id)
        
            self.log.info("Setup guild database done!")

    @tasks.loop(seconds=60.0)
    async def status(self):
        status = settings['game_activity']
        random_activity = choice(status)
        
        match random_activity['activity']:
            case "game":
                await self.change_presence(activity=discord.Game(name=random_activity['name']))
            case "listening":
                await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening,
                                                                     name=random_activity['name']))
            case "watching":
                await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,
                                                                     name=random_activity['name']))

    async def setup_hook(self):
        for extend in settings['extension']:
            await self.load_extension(extend)
            self.log.info(f"Load - {extend}")
        self.tree.copy_global_to(guild=discord.Object(id=settings["main_guild"]))
        await self.tree.sync(guild=discord.Object(id=settings["main_guild"]))
        self.log.info(f"Synced slash commands for {self.user}")

    async def setup_emoji(self):
        channel_db = role_db.db_channel_id()
        if len(channel_db) == 0:
            return
        for row in channel_db:
            channel = self.get_channel(row[0])
            message = await channel.fetch_message(row[1])
            await message.add_reaction(row[2])
    
    async def on_ready(self):
        await self.setup_bot()
        print(f"Буп!\nВы вошли как {self.user}")
        self.status.start()
        self.remove_command("help")
        try:
            await self.setup_emoji()
        except Exception as e:
            self.log.error(e)


client = DiscordClient()
        
