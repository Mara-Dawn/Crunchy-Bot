import discord

from datalayer.garden import FlashBeanPlant, Plot, UserGarden, YellowBeanPlant


class PlotEmbed(discord.Embed):

    def __init__(
        self,
        plot: Plot,
    ):
        plot_nr = UserGarden.PLOT_ORDER.index((plot.x, plot.y))
        last_watered = plot.get_hours_since_last_water()
        last_fertilized = plot.modifiers.last_fertilized
        last_flash_bean = plot.get_hours_since_last_flash_bean()
        flash_beans_active = plot.get_active_flash_bean_count()
        ready_timestamp = plot.get_estimated_harvest_datetime()

        plant_name = None
        if plot.plant is not None:
            plant_name = plot.plant.type.value

        title = "Empty Plot"
        if plant_name is not None:
            title = f"{plant_name}"

        description = f"**Plot {plot_nr + 1} - Row: {plot.y+1}, Column: {plot.x+1}**\n"

        if ready_timestamp is not None:
            description += (
                f"*Estimated to be ready <t:{int(ready_timestamp.timestamp())}:R>*\n"
            )
        if last_watered is not None and plot.plant.allow_modifiers:
            description += (
                f"*{int(last_watered)} hours since this plot was last watered.*\n"
            )
        if last_fertilized is not None:
            fertilizer_left = YellowBeanPlant.MODIFIER_DURATON - last_fertilized
            if fertilizer_left >= 0:
                description += (
                    f"*The fertilizer will run out in {int(fertilizer_left)} hours*\n"
                )
        if last_flash_bean is not None:
            flash_bean_left = FlashBeanPlant.MODIFIER_DURATON - last_flash_bean
            if flash_bean_left >= 0:
                description += (
                    f"*Flash bean buff will run out in {int(flash_bean_left)} hours*\n"
                )
        if flash_beans_active > 1:
            description += (
                f"*You currently have {flash_beans_active} active Flash Beans*\n"
            )

        if plant_name is None:
            description += (
                "* **Watered** plants grow **twice as fast.**\n"
                "* A plot will stay **wet for 24 hours**.\n"
                "* **Harvesting** gives you an **additional plot**\n."
            )
        super().__init__(
            title=title,
            color=discord.Colour.purple(),
            description=description,
        )
        self.set_image(url="attachment://status.png")
