import discord
import wavelink
import typing
import logging
import re
import asyncio
import datetime as dt
from discord.ext import commands
from discord import app_commands
from core.settings_bot import config

TIME_REGEX = r"([0-9]{1,2})[:ms](([0-9]{1,2})s?)?"
URL_REGEX = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s(" \
            r")<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’])) "


class CustomPlayer(wavelink.Player):
    def __init__(self):
        super().__init__()
        self.queue = wavelink.Queue()


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.log = logging.getLogger(f'LunaBOT.{__name__}')
        self.channel = {}
        bot.loop.create_task(self.create_node())

    async def create_node(self):
        await self.bot.wait_until_ready()
        await wavelink.NodePool.create_node(bot=self.bot, host="127.0.0.1", port="2333", password="youshallnotpass",
                                            region="europe")

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        self.log.info(f"Node: <{node.identifier}> is now Ready!")

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: CustomPlayer, track: wavelink.Track, reason):
        channel = self.channel.get(f"{player.guild.id}")

        if reason == "STOPPED":
            player.queue.clear()

        if not player.queue.is_empty:
            next_track = player.queue.get()
            await player.play(next_track)
            fin_embed = discord.Embed(
                color=discord.Color.blurple(),
                timestamp=dt.datetime.utcnow()
            )
            fin_embed.set_author(name="Now playing:", icon_url=self.bot.user.avatar)
            fin_embed.add_field(name="Track title",
                                value=f"[{next_track.info['title']}]({next_track.info['uri']})",
                                inline=False)
            fin_embed.set_thumbnail(
                url=f"https://img.youtube.com/vi/{next_track.info['identifier']}/maxresdefault.jpg")
            fin_embed.add_field(name="Artist", value=next_track.info['author'], inline=True)
            t_sec = int(next_track.length)
            hour = int(t_sec / 3600)
            mins = int((t_sec % 3600) / 60)
            sec = int((t_sec % 3600) % 60)
            length = f"{hour}:{mins}:{sec:02}" if not hour == 0 else f"{mins}:{sec:02}"
            fin_embed.add_field(name="Length", value=f"{length}", inline=True)
            await channel.send(embed=fin_embed)
        else:
            if reason == "FINISHED":
                fin_embed = discord.Embed(color=discord.Color.blurple(),
                                          timestamp=dt.datetime.utcnow(),
                                          description="To extend, order more music through the `/play` command"
                                          )
                fin_embed.set_author(name="Queue is over..", icon_url=self.bot.user.avatar)
                await channel.send(embed=fin_embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.bot and after.channel is None:
            if not [m for m in before.channel.members if not m.bot]:
                node = wavelink.NodePool.get_node()
                player = node.get_player(member.guild)
                if player:
                    await player.disconnect()
                    self.channel.pop(f"{member.guild.id}")
        elif member.bot and before.channel:
            if not [m for m in before.channel.members if m is None]:
                return
            node = wavelink.NodePool.get_node()
            player = node.get_player(member.guild)
            await player.disconnect()
            self.channel.pop(f"{member.guild.id}")

    @app_commands.command(name="join", description="Connection to the voice channel")
    async def join_voice(self, interaction: discord.Integration, channel: typing.Optional[discord.VoiceChannel] = None):
        if channel is None:
            try:
                member = interaction.guild.get_member(interaction.user.id)
                channel = member.voice.channel
            except AttributeError as e:
                return await interaction.response.send_message("Failed to connect...", ephemeral=True)

        node = wavelink.NodePool.get_node()
        player = node.get_player(interaction.guild)

        if player is not None:
            if player.is_connected():
                return await interaction.response.send_message("Bot is already connected to a voice channel",
                                                               ephemeral=True)

        await channel.connect(cls=CustomPlayer())
        await interaction.response.send_message(f"Bot connect to the voice {channel.name}", ephemeral=True)

    @app_commands.command(name="leave", description="Disconnect to the voice channel")
    async def leave_voice(self, interaction: discord.Integration):
        node = wavelink.NodePool.get_node()
        player = node.get_player(interaction.guild)

        if player is None:
            return await interaction.response.send_message("Bot is not connected to any voice channel", ephemeral=True)

        member = interaction.guild.get_member(interaction.user.id)
        member_bot = interaction.guild.get_member(self.bot.user.id)
        channel = member.voice

        if channel is None:
            return await interaction.response.send_message(
                "You cannot use the command without being in the voice channel.", ephemeral=True)
        elif channel.channel.id != member_bot.voice.channel.id:
            return await interaction.response.send_message(
                "You cannot use the command without being in the voice channel.", ephemeral=True)

        await player.disconnect()
        await interaction.response.send_message("Disconnected..", ephemeral=True)

    @app_commands.command(name="play", description="Staring play sound from URL")
    async def play_command(self, interaction: discord.Integration, query: str):
        try:
            search = await wavelink.YouTubeTrack.search(query=query)
        except Exception as e:
            self.log.warning(f"Exception {e}")
            return await interaction.response.send_message("", embed=discord.Embed(
                title="Something went wrong while searching for this track",
                color=discord.Color.red()
            ))

        if search is None:
            return await interaction.response.send_message("No tracks found")
        try:
            mbed = discord.Embed(
                description=("\n".join(f"**{i + 1}. {t.title}**" for i, t in enumerate(search[:5]))),
                color=discord.Color.blurple(),
                timestamp=dt.datetime.utcnow()
            )
            avatar = interaction.user.avatar.url
            mbed.set_author(url=avatar, name="Select the track: ")
        except TypeError as e:
            self.log.warning(f"Exception {e}")
            embed_error = discord.Embed(color=discord.Color.red(),
                                        timestamp=dt.datetime.utcnow(),
                                        title="The `/play` command cannot work with playlists, use `/playlistadd`"
                                        )
            embed_error.set_author(name="Something went wrong..", icon_url=interaction.user.avatar)
            return await interaction.response.send_message(embed=embed_error)

        await interaction.response.send_message("", embed=mbed)
        msg = await interaction.original_response()
        channel = self.bot.get_channel(msg.channel.id)
        member = interaction.guild.get_member(interaction.user.id)

        if member.voice is None:
            return await msg.edit(content=f"first go to the voice channel, and then order the track",
                                  delete_after=15
                                  )

        emojis_list = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '❌']
        emojis_dict = {
            '1️⃣': 0,
            "2️⃣": 1,
            "3️⃣": 2,
            "4️⃣": 3,
            "5️⃣": 4,
            "❌": -1
        }

        for emoji in list(emojis_list[:min(len(search), len(emojis_list))]):
            await msg.add_reaction(emoji)

        def check(res, user):
            return res.emoji in emojis_list and user == interaction.user and res.message.id == msg.id

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await msg.delete()
            return
        else:
            await msg.delete()

        try:
            if emojis_dict[reaction.emoji] == -1: return
            choosed_track = search[emojis_dict[reaction.emoji]]
        except Exception as e:
            return self.log.error(e)

        if not interaction.guild.voice_client:
            custom_player = CustomPlayer()
            vc: wavelink.Player = await member.voice.channel.connect(cls=custom_player)
        else:
            vc: wavelink.Player = interaction.guild.voice_client

        if self.channel.get(f"{interaction.guild.id}") is None:
            self.channel.update({f"{interaction.guild.id}": channel})

        if vc.is_playing():
            vc.queue.put(item=choosed_track)
            embed_queue = discord.Embed(color=discord.Color.blurple(),
                                        description=f"This added track in the queue\n "
                                                    f"Number of music in the queue: **{len(vc.queue)}**",
                                        timestamp=dt.datetime.utcnow())
            embed_queue.set_author(name=f"🎵 Add queue {choosed_track.title}", url=choosed_track.uri,
                                   icon_url=interaction.user.avatar)
            embed_queue.set_thumbnail(url=choosed_track.thumb)
            await channel.send("", embed=embed_queue)
        else:
            try:
                await vc.play(choosed_track)
            except Exception as e:
                self.log.error(e)
                return await channel.send("", embed=discord.Embed(
                    title="Something went wrong while searching for this track",
                    color=discord.Color.red()
                ))

            embed_play = discord.Embed(color=discord.Color.blurple(), timestamp=dt.datetime.utcnow())
            embed_play.set_thumbnail(url=choosed_track.thumb)
            embed_play.set_author(name=f"Playing now {choosed_track}", url=choosed_track.uri,
                                  icon_url=interaction.user.avatar)
            embed_play.add_field(name="Artist:", value=f"{choosed_track.author}", inline=False)
            embed_play.add_field(name="Volume player:", value=f"{vc.volume} %")
            t_sec = int(choosed_track.length)
            print(t_sec)
            hour = int(t_sec / 3600)
            mins = int((t_sec % 3600) / 60)
            sec = int((t_sec % 3600) % 60)
            length = f"{hour}:{mins}:{sec:02}" if not hour == 0 else f"{mins}:{sec:02}"
            embed_play.add_field(name="Length:", value=f"{length}")
            await channel.send("", embed=embed_play)

    @app_commands.command(name="stop", description="Stop playing sound")
    async def stop_command(self, interaction: discord.Integration):
        node = wavelink.NodePool.get_node()
        player = node.get_player(interaction.guild)

        if player is None:
            return await interaction.response.send_message("Bot is not connected to any voice channel", ephemeral=True)

        if player.is_playing:
            await player.stop()
            embed = discord.Embed(color=discord.Colour.blurple(),
                                  timestamp=dt.datetime.utcnow(),
                                  description="You stopped the player, so you can start it again using `/play`"
                                  )
            embed.set_author(name="Playback Stopped ⏹", icon_url=interaction.user.avatar)
            await interaction.response.send_message("", embed=embed)
        else:
            return await interaction.response.send_message("Nothing Is playing right now", ephemeral=True)

    @app_commands.command(name="pause", description="Paused playback")
    async def pause_command(self, interaction: discord.Integration):
        node = wavelink.NodePool.get_node()
        player = node.get_player(interaction.guild)

        if player is None:
            return await interaction.response.send_message("Bot is not connected to any voice channel", ephemeral=True)

        if not player.is_paused():
            if player.is_playing():
                await player.pause()
                embed = discord.Embed(color=discord.Color.blurple(),
                                      timestamp=dt.datetime.utcnow(),
                                      description="The player is paused, to return it to work, use the `/resume` command")
                embed.set_author(name="Playback Paused ⏸", icon_url=interaction.user.avatar)
                await interaction.response.send_message("", embed=embed)
            else:
                return await interaction.response.send_message("Nothing Is playing right now", ephemeral=True)
        else:
            return await interaction.response.send_message("Playback is Already paused", ephemeral=True)

    @app_commands.command(name="resume", description="Playback resumed")
    async def resume_command(self, interaction: discord.Integration):
        node = wavelink.NodePool.get_node()
        player = node.get_player(interaction.guild)

        if player is None:
            return await interaction.response.send_message("Bot is not connected to any voice channel", ephemeral=True)

        if player.is_paused():
            await player.resume()
            embed = discord.Embed(color=discord.Color.blurple(),
                                  description="Player is resume..", timestamp=dt.datetime.utcnow())
            embed.set_author(name=f"Keeps playing", icon_url=interaction.user.avatar)
            return await interaction.response.send_message("", embed=embed)
        else:
            if not len(player.queue) == 0:
                track: wavelink.track = player.queue[0]
                await player.play(track)
                ebed = discord.Embed(
                    color=discord.Color.blurple(),
                    description="Player is resume..",
                    timestamp=dt.datetime.utcnow()
                )
                ebed.set_author(name=f"Now playing: {track.title}", icon_url=interaction.user.avatar)
                return await interaction.response.send_message("", embed=ebed)
            else:
                return await interaction.response.send_message("Playblack is not paused", ephemeral=True)

    @app_commands.command(name="volume", description="Playback volume")
    async def volume_command(self, interaction: discord.Integration, to: int):
        if to > 100:
            return await interaction.response.send_message("Volume should between 0 and 100")
        elif to < 1:
            return await interaction.response.send_message("Volume should between 0 and 100")

        node = wavelink.NodePool.get_node()
        player = node.get_player(interaction.guild)

        await player.set_volume(to)
        embed = discord.Embed(title=f"Changed Volume to {to}", color=discord.Color.blurple())
        await interaction.response.send_message("", embed=embed)

    @app_commands.command(name="seek", description="Seek to the given position in the song.")
    async def seek_command(self, interaction: discord.Integration, seek: str):
        node = wavelink.NodePool.get_node()
        player = node.get_player(interaction.guild)

        if player is None:
            return await interaction.response.send_message("Bot is not connected to any voice channel", ephemeral=True)

        if not (match := re.match(TIME_REGEX, seek)):
            return await interaction.response.send_message("Time code invalid", ephemeral=True)

        if match.group(3):
            secs = (int(match.group(1)) * 60) + (int(match.group(3)))
        else:
            secs = int(match.group(1))

        await player.seek(secs * 1000)
        await interaction.response.send_message("Seeked", ephemeral=True)

    @app_commands.command(name="nowplaying", description="Now playing sound")
    async def now_play_command(self, interaction: discord.Integration):
        node = wavelink.NodePool.get_node()
        player = node.get_player(interaction.guild)

        if player is None:
            return await interaction.response.send_message("Bot is not connected to any voice channel")

        if player.is_playing():
            mbed = discord.Embed(
                color=discord.Colour.blurple(),
                timestamp=dt.datetime.utcnow()
            )
            mbed.set_author(name="Now playing:", icon_url=interaction.user.avatar)
            print(f"{player.track.info}")
            mbed.add_field(name="Track title", value=f"[{player.track.info['title']}]({player.track.info['uri']})",
                           inline=False)
            mbed.set_thumbnail(url=f"https://img.youtube.com/vi/{player.track.info['identifier']}/maxresdefault.jpg")
            mbed.add_field(name="Artist", value=player.track.info['author'], inline=True)
            t_sec = int(player.track.length)
            hour = int(t_sec / 3600)
            mins = int((t_sec % 3600) / 60)
            sec = int((t_sec % 3600) % 60)
            length = f"{hour}:{mins}:{sec:02}" if not hour == 0 else f"{mins}:{sec:02}"
            pos_sec = int(player.position)
            hour_pos = int(pos_sec / 3600)
            mins_pos = int((pos_sec % 3600) / 60)
            sec_pos = int((pos_sec % 3600) % 60)
            position = f"{hour_pos}:{mins_pos}:{sec_pos:02}" if not hour == 0 else f"{mins_pos}:{sec_pos:02}"
            mbed.add_field(name="Length", value=f"{length}/{position}", inline=True)
            mbed.add_field(name="Volume Music", value=f"{player.volume}%", inline=True)
            if player.is_paused():
                text_paused = "Paused ⏸"
            else:
                text_paused = "Playing ▶"
            mbed.add_field(name="Player status", value=text_paused)

            return await interaction.response.send_message(embed=mbed)
        else:
            return await interaction.response.send_message("Nothing is playing right now", ephemeral=True)

    @app_commands.command(name="skip", description="Skip playing music")
    async def skip_command(self, interaction: discord.Integration):
        node = wavelink.NodePool.get_node()
        player = node.get_player(interaction.guild)
        if player:
            if not player.is_playing():
                return await interaction.response.send_message("Nothing is playing", ephemeral=True)
            if player.queue.is_empty:
                return await player.stop()

            await player.seek(player.track.length * 1000)

            mbed = discord.Embed(color=discord.Colour.blurple(),
                                 timestamp=dt.datetime.utcnow(),
                                 description=f"Track: [{player.track.info['title']}]({player.track.info['uri']}) has skip!"
                                 )
            mbed.set_author(name=f"User {interaction.user.display_name} skipped track",
                            icon_url=interaction.user.avatar)

            await interaction.response.send_message(embed=mbed)
            if player.is_paused():
                await player.resume()
        else:
            return await interaction.response.send_message("Bot is not connected to any voice channel")

    @app_commands.command(name="queue", description="Show queue list")
    async def queue_command(self, interaction: discord.Integration):
        node = wavelink.NodePool.get_node()
        player = node.get_player(interaction.guild)

        if player is None:
            return await interaction.response.send_message("Bot is not connected to any voice channel")

        if not player.queue.is_empty:
            queue_list = player.queue
            mbed = discord.Embed(
                description="\n".join(f"**{i + 1}. {track}**" for i, track in enumerate(queue_list)),
                color=discord.Color.blurple(),
                timestamp=dt.datetime.utcnow()
            )
            mbed.set_author(icon_url=interaction.user.avatar,
                            name=f"Now playing {player.track}" if player.is_playing() else "Queue: ")
            return await interaction.response.send_message(embed=mbed)
        else:
            return await interaction.response.send_message("The queue is empty", ephemeral=True)

    @app_commands.command(name="playlistadd", description="Playing playlist on YouTube")
    async def playlist_play_command(self, interaction: discord.Integration, playlist: str):
        try:
            search_playlist = await wavelink.YouTubeTrack.search(query=playlist)
        except Exception as e:
            self.log.warning(f"Exception {e}")
            return await interaction.response.send_message("", embed=discord.Embed(
                title="Something went wrong while searching for this track",
                color=discord.Color.red()
            ))
        member = interaction.guild.get_member(interaction.user.id)

        if member.voice is None:
            return await interaction.response.send_message("Go to voice chat, and then use this command again", ephemeral=True)

        if not interaction.guild.voice_client:
            custom_player = CustomPlayer()
            vc: wavelink.Player = await member.voice.channel.connect(cls=custom_player)
        else:
            vc: wavelink.Player = interaction.guild.voice_client

        for tracks in search_playlist.tracks:
            vc.queue.put(item=tracks)

        if vc.is_playing():
            embed_queue = discord.Embed(color=discord.Color.blurple(),
                                        description=f"This added track in the queue\n "
                                                    f"Number of music in the queue: **{len(vc.queue)}**",
                                        timestamp=dt.datetime.utcnow())
            embed_queue.set_author(name=f"🎵 Add queue playlist {search_playlist.name}", url=playlist,
                                   icon_url=interaction.user.avatar)
            embed_queue.set_thumbnail(url=search_playlist.tracks[0].thumb)
            await interaction.response.send_message("", embed=embed_queue)
        else:
            try:
                await vc.play(vc.queue.get())
                embed_queue = discord.Embed(color=discord.Color.blurple(),
                                            description=f"This added track in the queue\n "
                                                        f"Number of music in the queue: **{len(vc.queue)}**",
                                            timestamp=dt.datetime.utcnow())
                embed_queue.set_author(name=f"🎵 Add queue playlist {search_playlist.name}", url=playlist,
                                       icon_url=interaction.user.avatar)
                embed_queue.set_thumbnail(url=search_playlist.tracks[0].thumb)
                await interaction.response.send_message("", embed=embed_queue)
                msg = await interaction.original_response()
                channel = self.bot.get_channel(msg.channel.id)

                embed_play = discord.Embed(color=discord.Color.blurple(), timestamp=dt.datetime.utcnow())
                embed_play.set_thumbnail(url=search_playlist.tracks[0].thumb)
                embed_play.set_author(name=f"Playing now {search_playlist.tracks[0].title}",
                                      url=search_playlist.tracks[0].uri,
                                      icon_url=interaction.user.avatar)
                embed_play.add_field(name="Artist:", value=f"{search_playlist.tracks[0].author}", inline=False)
                embed_play.add_field(name="Volume player:", value=f"{vc.volume} %")
                t_sec = int(search_playlist.tracks[0].length)
                print(t_sec)
                hour = int(t_sec / 3600)
                mins = int((t_sec % 3600) / 60)
                sec = int((t_sec % 3600) % 60)
                length = f"{hour}:{mins}:{sec:02}" if not hour == 0 else f"{mins}:{sec:02}"
                embed_play.add_field(name="Length:", value=f"{length}")
                await channel.send(embed=embed_play)

                if self.channel.get(f"{interaction.guild.id}") is None:
                    self.channel.update({f"{interaction.guild.id}": channel})

            except Exception as e:
                self.log.error(e)
                return await interaction.response.send_message("", embed=discord.Embed(
                    title="Something went wrong while searching for this track",
                    color=discord.Color.red()
                ))


async def setup(bot: commands.Bot):
    settings = config()
    await bot.add_cog(Music(bot), guilds=[discord.Object(id=settings['main_guild'])])
