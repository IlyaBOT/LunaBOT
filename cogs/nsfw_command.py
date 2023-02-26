import enum
import discord
import logging
import datetime as dt
from discord import app_commands
from discord.ext import commands
from core.e621 import E621connect
from core.settings_bot import config, CustomChecks


class SearchType(enum.Enum):
    webm = "webm"
    gif = "gif"
    png = "png"
    jpg = "jpg"


class NsfwCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.log = logging.getLogger(f"LunaBOT.{__name__}")
        self.e621api = E621connect()

    @app_commands.command(name="e621", description="Get post from site e621.net")
    @app_commands.check(CustomChecks.app_is_nsfw)
    async def e621(self, interaction: discord.Interaction, tags: str = None, type: SearchType = None):
        await interaction.response.send_message("Connecting to e621...")
        msg = await interaction.original_response()
        if tags is not None:
            tags_s = tags.split(" ")
            if len(tags_s) > 1:
                tag = "+".join(tags_s)
            else:
                tag = tags_s[0]

            if type is not None:
                type_url = f"+type%3A{type.name}"
                tag = tag + type_url

            data = await self.e621api.get_random_post_by_tag(tag)
            if data is None:
                return await msg.edit(content="Nothing found for this tag :(")

            image = data['file']['url']
            sample = data['sample']['url']
            id_post = data['id']
            score_up = data['score']['up']
            score_down = data['score']['down']
            rating = data['rating']

            file_ext = ["webm", "mp4", "gif", "swf"]
            if image.split('.')[-1] in file_ext:
                embed = discord.Embed(
                    title="Rawr! | Webw, mp4, Gif, or Swf format detected in post",
                    description=f" 🔞 e621 image found for **`{tags}`** 🔞\n\n"
                                f"**Score:** ⬆{score_up}/{score_down}⬇ | **rating:** `{rating}`\n\n"
                                f"**Post URL:** [Link](https://e621.net/posts/{id_post}) **Video URL:** [Link]({image})",
                    colour=discord.Colour.blue(),
                    timestamp=dt.datetime.utcnow()
                )
                embed.set_image(url=sample)
                return await msg.edit(content="", embed=embed)

            embed2 = discord.Embed(
                title="Rawr!",
                description=f" 🔞 e621 image found for **`{tags}`** 🔞\n"
                            f"**Score:** ⬆ {score_up} / {score_down} ⬇ | **rating:** `{rating}`\n\n"
                            f"**Post URL:** [Link](https://e621.net/posts/{id_post})",
                color=discord.Colour.blue(),
                timestamp=dt.datetime.utcnow()
            )
            embed2.set_image(url=image)
            await msg.edit(content="", embed=embed2)

        else:
            if type is not None:
                type_url = f"+type%3A{type.name}"
                data = await self.e621api.get_random_post(type_url)
            else:
                data = await self.e621api.get_random_post()

            if data is None:
                return await msg.edit(content="Failed to get post :(")

            image = data['file']['url']
            sample = data['sample']['url']
            id_post = data['id']
            score_up = data['score']['up']
            score_down = data['score']['down']
            rating = data['rating']

            file_ext = ["webm", "mp4", "gif", "swf"]
            if image.split('.')[-1] in file_ext:
                embed = discord.Embed(
                    title="Rawr! | Webw, mp4, Gif, or Swf format detected in post",
                    description=f" 🔞 e621 image found for **`Random`** 🔞\n\n"
                                f"**Score:** ⬆{score_up}/{score_down}⬇ | **rating:** `{rating}`\n\n"
                                f"**Post URL:** [Link](https://e621.net/posts/{id_post}) **Video URL:** [Link]({image})",
                    colour=discord.Colour.blue(),
                    timestamp=dt.datetime.utcnow()
                )
                embed.set_image(url=sample)
                return await msg.edit(content="", embed=embed)

            embed2 = discord.Embed(
                title="Rawr!",
                description=f" 🔞 e621 image found for **`Random`** 🔞\n"
                            f"**Score:** ⬆ {score_up} / {score_down} ⬇ | **rating:** `{rating}`\n\n"
                            f"**Post URL:** [Link](https://e621.net/posts/{id_post})",
                color=discord.Colour.blue(),
                timestamp=dt.datetime.utcnow()
            )
            embed2.set_image(url=image)
            await msg.edit(content="", embed=embed2)


async def setup(bot: commands.Bot):
    settings = config()
    await bot.add_cog(NsfwCommand(bot), guilds=[discord.Object(id=settings['main_guild'])])


