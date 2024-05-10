import discord
from datalayer.garden import UserGarden
from discord.ext import commands


class GardenEmbed(discord.Embed):

    def __init__(
        self,
        bot: commands.Bot,
        garden: UserGarden,
        author: str,
    ):
        super().__init__(
            title="Bean Garden",
            color=discord.Colour.purple(),
            description="Your very own peaceful garden.",
        )
        self.set_author(name=author, icon_url="attachment://profile_picture.png")

        message = ""
        for plot in garden.plots:
            if plot.x == 0:
                message += "\n"
            message += str(bot.get_emoji(plot.get_status_emoji()))

        self.add_field(name="Plot Overview:", value=message)
