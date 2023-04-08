import discord
from asyncio import sleep
from discord import Embed
from core.i18n import translate

class LangMessageable:
    @staticmethod
    async def mod_send(ctx, message, format=None ,file=None, reply_to=None):
        _ = translate(ctx.guild.id)

        if format is not None:
            message = _(message) % format
        else:
            message = _(message)
            
        if file is not None and reply_to is not None:
            await ctx.send(message, file=file, reference=reply_to.to_reference())
        elif file is not None:
            await ctx.send(message, file=file)
        elif reply_to is not None:
            await ctx.send(message, reference=reply_to.to_reference())
        elif file is not None and reply_to is not None:
            await ctx.send(message, file=file, reference=reply_to.to_reference())
        elif file is not None:
            await ctx.send(message, file=file)
        elif reply_to is not None:
            await ctx.send(f"{reply_to.author.mention}, {message}")
        else:
            await ctx.send(message)


    @staticmethod
    async def send_embed(ctx, title=None, description=None, color=None, author=None, image=None, footer=None, fields=None, format=None, thumbnail=None, vi=None):
        _ = translate(ctx.guild.id)
        embed = Embed()
        if title is not None and format is not None:
            if format.get('title'):
                embed.title = _(title) % (format.get('title'))
            else:
                embed.title = _(title)
        elif title is not None:
            embed.title = _(title)


        if description is not None and format is not None:
            if format.get('description'):
                embed.description = _(description) % (format.get('description'))
            else:
                embed.description = _(description)
        elif description is not None:
             embed.description = _(description)

        if color is not None:
            embed.colour = color


        if image is not None:
            embed.set_image(image=image)

        if footer is not None:
            embed.set_footer(
                icon_url=_(footer.get('icon')),
                text=_(footer.get('text')),
            )

        if author is not None:
            if author.get("format"):
                name_author = _(author.get('name')) % (author.get('format'))
            else:
                name_author = _(author.get('name'))
            embed.set_author(
                name=name_author,
                url=_(author.get('url')),
                icon_url=_(author.get('icon'))
            )

        if thumbnail is not None:
            embed.set_thumbnail(url=thumbnail)

        if fields is not None and len(fields) < 25:
            for field in fields:
                if field.get('format_name'):
                    name = _(field.get('name')) % (field['format_name'])
                else:
                    name = _(field.get('name'))
                
                if field.get('format_value'):
                    value = _(field.get('value')) % (field['format_value'])
                else:
                    value = _(field.get('value'))
      
                embed.add_field(
                            name=name,
                            value=value,
                            inline=field.get('inline')
                        )

        
        if vi is not None:
            return await ctx.send("", embed=embed, view=vi)
        else:
            return await ctx.send("", embed=embed)
    

    @staticmethod
    async def app_send_embed(
        interaction, 
        title=None, 
        description=None, 
        color=None, 
        author=None, 
        image=None, 
        footer=None, 
        fields=None, 
        format=None, 
        thumbnail=None, 
        ephemeral=False,
        view=None
        ):
        _ = translate(interaction.guild.id)
        embed = Embed()
        if title is not None and format is not None:
            if format.get('title'):
                embed.title = _(title) % (format.get('title'))
            else:
                embed.title = _(title)
        elif title is not None:
            embed.title = _(title)


        if description is not None and format is not None:
            if format.get('description'):
                embed.description = _(description) % (format.get('description'))
            else:
                embed.description = _(description)
        elif description is not None:
            embed.description = _(description)

        if color is not None:
            embed.colour = color


        if image is not None:
            embed.set_image(image=image)

        if footer is not None:
            embed.set_footer(
                icon_url=_(footer.get('icon')),
                text=_(footer.get('text')),
            )

        if author is not None:
            if author.get("format"):
                name_author = _(author.get('name')) % (author.get('format'))
                print(author.get('format'))
            else:
                name_author = _(author.get('name'))
            embed.set_author(
                name=name_author,
                url=_(author.get('url')),
                icon_url=_(author.get('icon'))
            )

        if thumbnail is not None:
            embed.set_thumbnail(url=thumbnail)

        if fields is not None and len(fields) < 25:
            for field in fields:
                if field.get('format_name'):
                    name = _(field.get('name')) % (field['format_name'])
                else:
                    name = _(field.get('name'))
                
                if field.get('format_value'):
                    value = _(field.get('value')) % (field['format_value'])
                else:
                    value = _(field.get('value'))
      
                embed.add_field(
                            name=name,
                            value=value,
                            inline=field.get('inline')
                        )

        
        if view is not None:
            return await interaction.response.send_message("", embed=embed, view=view, ephemeral=ephemeral)
        else:
            return await interaction.response.send_message("", embed=embed, ephemeral=ephemeral)
    
    @staticmethod
    async def app_mod_send(interaction, message, format=None ,file=None, ephemeral=False):
        _ = translate(interaction.guild.id)

        if format is not None:
            message = _(message) % format
        else:
            message = _(message)
            
        if file is not None:
            await interaction.response.send_message(message, file=file, ephemeral=ephemeral)
        else:
            await interaction.response.send_message(message, ephemeral=ephemeral)

    @staticmethod
    async def mod_edit(msg, content=None, file=None, format=None, delete_after=None):
        _ = translate(msg.channel.guild.id)

        if format is not None:
            content = _(content) % format
        else:
            content = _(content)

        if file is not None:
            await msg.edit(content=content, file=file, embed=None)
        else:
            await msg.edit(content=content, embed=None)

        if delete_after is not None:
            await sleep(delete_after)
            await msg.delete()


        
  