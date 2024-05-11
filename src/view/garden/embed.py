import discord
from datalayer.garden import UserGarden
from discord.ext import commands


class GardenEmbed(discord.Embed):

    def __init__(
        self,
        bot: commands.Bot,
        garden: UserGarden,
    ):
        description = "Your very own peaceful garden."

        super().__init__(
            title="Bean Garden",
            color=discord.Colour.purple(),
            description=description,
        )
        self.garden = garden
        self.bot = bot

    def get_garden_content(self) -> str:
        message = ""
        for plot in self.garden.plots:
            if plot.x == 0:
                message += "\n"
            message += str(self.bot.get_emoji(plot.get_status_emoji()))
        return message
