import discord
from discord.ext import commands

from datalayer.garden import UserGarden


class GardenEmbed(discord.Embed):

    def __init__(
        self,
        bot: commands.Bot,
        garden: UserGarden,
    ):
        description = "Your very own peaceful garden.\n"

        next_harvest = garden.get_next_harvest_plot()
        next_watering = garden.get_next_water_plot()

        if next_harvest is not None:
            plot_nr = garden.get_plot_number(next_harvest)
            timestamp = int(next_harvest.get_estimated_harvest_datetime().timestamp())
            description += f"\nNext Harvest: Plot {plot_nr} <t:{timestamp}:R>"

        if next_watering is not None:
            plot_nr = garden.get_plot_number(next_watering)
            hours = 24 - next_watering.get_hours_since_last_water()
            timestamp = int(next_watering.get_dry_datetime().timestamp())
            if hours > 0:

                description += (
                    f"\nDriest Plot: Plot {plot_nr} will be dry <t:{timestamp}:R>."
                )
            else:
                description += f"\nDriest Plot: Plot {plot_nr} needs water."

        super().__init__(
            title="Bean Garden",
            color=discord.Colour.purple(),
            description=description,
        )
        self.garden = garden
        self.bot = bot

    def get_garden_content(self) -> str:
        rows = [[], [], [], [], []]
        for plot in self.garden.plots:
            rows[plot.y].append(str(self.bot.get_emoji(plot.get_status_emoji())))
        rows_text = ["".join(row) for row in rows]
        return "\n".join(rows_text)
