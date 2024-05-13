import discord
from discord.ext import commands


class CatalogEmbed(discord.Embed):

    ITEMS_PER_PAGE = 6

    def __init__(
        self,
        bot: commands.Bot,
    ):
        super().__init__(
            title="Item Catalog",
            color=discord.Colour.purple(),
            description="A list of all Items and where to obtain them.",
        )
        author_name = bot.user.display_name
        author_img = bot.user.display_avatar
        self.set_author(name=author_name, icon_url=author_img)
