import discord
from datalayer.garden import UserGarden


class PlotEmbed(discord.Embed):

    def __init__(
        self,
        plot_nr: int,
        x: int,
        y: int,
    ):
        description = (
            "* **Watered** plants grow **twice as fast.**\n"
            "* A plot will stay **wet for 24 hours**.\n"
            f"* **Harvesting** gives you an **additional plot** (max {UserGarden.MAX_PLOTS})."
        )
        super().__init__(
            title=f"Plot {plot_nr + 1} - Row: {y+1}, Column: {x+1}",
            color=discord.Colour.purple(),
            description=description,
        )
        self.set_image(url="attachment://status.png")
