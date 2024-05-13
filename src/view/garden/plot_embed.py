import discord
from datalayer.garden import Plot, UserGarden, YellowBeanPlant


class PlotEmbed(discord.Embed):

    def __init__(
        self,
        plot: Plot,
    ):
        plot_nr = UserGarden.PLOT_ORDER.index((plot.x, plot.y))
        last_watered = plot.hours_since_last_water()
        last_fertilized = plot.hours_since_last_fertilized()

        plant_name = None
        if plot.plant is not None:
            plant_name = plot.plant.type.value

        title = "Empty Plot"
        if plant_name is not None:
            title = f"{plant_name}"

        description = f"**Plot {plot_nr + 1} - Row: {plot.y+1}, Column: {plot.x+1}**\n"

        if last_watered is not None:
            description += f"*{last_watered} hours since this plot was last watered.*\n"
        if last_fertilized is not None:
            fertilizer_left = YellowBeanPlant.FERTILE_TIME - last_fertilized
            if fertilizer_left >= 0:
                description += (
                    f"*The fertilizer will run out in {fertilizer_left} hours*\n"
                )

        if plant_name is None:
            description += (
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
