import enum
import discord
import logging
import datetime as dt
from discord import app_commands
from discord.ext import commands
from core.e621 import E621connect
from core.derpibooru import DerpibooruConnect
from core.settings_bot import config, CustomChecks


class SearchType(enum.Enum):
    webm = "webm"
    gif = "gif"
    png = "png"
    jpg = "jpg"


class MyGroup(app_commands.Group):

    @app_commands.command(name="safe", description="Get post safe from Derpibooru")
    async def derpibooru_sfw(self, interaction: discord.Interaction, search: str):
        derpibooruapi = DerpibooruConnect()
        await interaction.response.send_message("Connect to derpibooru..")
        msg = await interaction.original_response()
        if search is not None:
            search_s = search.split(" ")
            if len(search_s) > 1:
                search_tag = "+".join(search_s)
            else:
                search_tag = search_s[0]

        data = await derpibooruapi.get_safe_post(tag=search_tag)
        if data is None:
            return await msg.edit(content="Nothing found for this tag :(")

        image = data.get('view_url')
        id_image = data.get('id')

        file_exc = ["webm", "mp4", "gif", "swf"]
        if image.split('.')[-1] in file_exc:
            embed = discord.Embed(
                title="Derpibooru posting",
                description=f"Derpibooru image found for **`{search}`** 🔞\n"
                            f"**Post URL:** [Link](https://derpibooru.org/images/{id_image}) **Video URL:** [Link]({image})",
                color=discord.Colour.dark_purple()
            )
            embed.set_image(url=image)
            return await msg.edit(content="", embed=embed)

        embed2 = discord.Embed(
            title="Derpibooru posting",
            description=f"Derpibooru image found for **`{search}`** 🔞\n"
                        f"**Post URL:** [Link](https://derpibooru.org/images/{id_image})",
            color=discord.Color.dark_purple()
        )
        embed2.set_image(url=image)
        await msg.edit(content="", embed=embed2)

    @app_commands.command(name="explicit", description="Get post explicit from Derpibooru")
    @app_commands.check(CustomChecks.app_is_nsfw)
    async def derpibooru_nsfw(self, interaction: discord.Interaction, search: str):
        derpibooruapi = DerpibooruConnect()
        await interaction.response.send_message("Connect to derpibooru..")
        msg = await interaction.original_response()
        if search is not None:
            search_s = search.split(" ")
            if len(search_s) > 1:
                search_tag = "%2C+".join(search_s)
            else:
                search_tag = search_s[0]

        data = await derpibooruapi.get_explicit_post(tag=search_tag)
        if data is None:
            return await msg.edit(content="Nothing found for this tag :(")

        image = data.get('view_url')
        id_image = data.get('id')

        file_exc = ["webm", "mp4", "gif", "swf"]
        if image.split('.')[-1] in file_exc:
            embed = discord.Embed(
                title="Derpibooru posting",
                description=f"Derpibooru image found for **`{search}`** 🔞\n"
                            f"**Post URL:** [Link](https://derpibooru.org/images/{id_image}) **Video URL:** [Link]({image})",
                color=discord.Colour.dark_purple()
            )
            embed.set_image(url=image)
            return await msg.edit(content="", embed=embed)

        embed2 = discord.Embed(
            title="Derpibooru posting",
            description=f"Derpibooru image found for **`{search}`** 🔞\n"
                        f"**Post URL:** [Link](https://derpibooru.org/images/{id_image})",
            color=discord.Color.dark_purple()
        )
        embed2.set_image(url=image)
        await msg.edit(content="", embed=embed2)


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
            id_post = data.get('id')
            score_up = data['score']['up']
            score_down = data['score']['down']
            rating = data.get('rating')

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
            id_post = data.get('id')
            score_up = data['score']['up']
            score_down = data['score']['down']
            rating = data.get('rating')

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
    bot.tree.add_command(MyGroup(name="derpibooru"))
    await bot.add_cog(NsfwCommand(bot), guilds=[discord.Object(id=settings['main_guild'])])


