import discord
from datalayer.garden import UserGarden


class PlotEmbed(discord.Embed):

    def __init__(
        self,
        plot_nr: int,
        x: int,
        y: int,
        plant_name: str = None,
    ):
        if plant_name is None:
            plant_name = "Empty Plot"
        title = f"{plant_name}"
        description = (
            f"**Plot {plot_nr + 1} - Row: {y+1}, Column: {x+1}**\n"
            "* **Watered** plants grow **twice as fast.**\n"
            "* A plot will stay **wet for 24 hours**.\n"
            f"* **Harvesting** gives you an **additional plot**\n(max {UserGarden.MAX_PLOTS})."
        )
        super().__init__(
            title=title,
            color=discord.Colour.purple(),
            description=description,
        )
        self.set_image(url="attachment://status.png")
