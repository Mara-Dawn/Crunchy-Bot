import contextlib

import discord
from discord.ext import commands

from control.controller import Controller
from control.types import ControllerType
from datalayer.garden import UserGarden
from datalayer.types import PlantType, PlotState
from events.types import UIEventType
from events.ui_event import UIEvent
from view.garden.embed import GardenEmbed
from view.garden.plot_embed import PlotEmbed
from view.view_menu import ViewMenu


class PlotView(ViewMenu):

    def __init__(
        self,
        controller: Controller,
        interaction: discord.Interaction,
        garden: UserGarden,
        x: int,
        y: int,
    ):
        super().__init__(timeout=None)

        self.controller = controller
        self.garden = garden
        self.x = x
        self.y = y
        self.plot = garden.get_plot(x, y)
        self.user_seeds = garden.user_seeds

        self.member_id = interaction.user.id
        self.guild_id = interaction.guild_id
        self.blocked = False

        self.selected_seed: PlantType = None

        if len(self.user_seeds) > 0:
            self.selected_seed = list(self.user_seeds.keys())[0]

        self.controller_types = [ControllerType.GARDEN_VIEW]
        self.controller.register_view(self)

        self.back_button: BackButton = None
        self.water_button: WaterButton = None
        self.plant_button: PlantButton = None
        self.harvest_button: HarvestButton = None
        self.destroy_button: DestroyButton = None
        self.seed_select: SeedSelect = None

        self.refresh_elements()

    async def listen_for_ui_event(self, event: UIEvent):
        if event.view_id != self.id:
            return

        match event.type:
            case UIEventType.GARDEN_REFRESH:
                garden = event.payload
                await self.refresh_ui(garden)
                self.blocked = False
            case UIEventType.GARDEN_PLOT_BLOCK:
                self.blocked = True
            case UIEventType.GARDEN_DETACH:
                self.controller.detach_view(self)
                self.stop()

    async def back_to_garden(self, interaction: discord.Interaction):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.GARDEN_PLOT_BACK,
            (interaction, self.message),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def water(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if self.blocked:
            return
        event = UIEvent(
            UIEventType.GARDEN_PLOT_WATER,
            (interaction, self.plot),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def plant(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if self.blocked:
            return
        event = UIEvent(
            UIEventType.GARDEN_PLOT_PLANT,
            (interaction, self.plot, self.selected_seed),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def remove(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if self.blocked:
            return
        event = UIEvent(
            UIEventType.GARDEN_PLOT_REMOVE,
            (interaction, self.plot),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def harvest(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if self.blocked:
            return
        event = UIEvent(
            UIEventType.GARDEN_PLOT_HARVEST,
            (interaction, self.plot),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def set_selected_seed(self, plant_type: PlantType):
        self.selected_seed = plant_type

    def refresh_elements(self):

        self.seed_select = None
        self.back_button = None
        self.water_button = None
        self.plant_button = None
        self.harvest_button = None
        self.destroy_button = None

        match self.plot.get_status():
            case PlotState.EMPTY:
                if len(self.user_seeds) > 0:
                    self.seed_select = SeedSelect(self.controller.bot, self.garden)
                self.plant_button = PlantButton()
                self.back_button = BackButton()
            case (
                PlotState.SEED_PLANTED
                | PlotState.GROWING
                | PlotState.SEED_PLANTED_WET
                | PlotState.GROWING_WET
            ):
                self.water_button = WaterButton()
                self.destroy_button = DestroyButton()
                self.back_button = BackButton()
            case PlotState.READY:
                self.harvest_button = HarvestButton()
                self.back_button = BackButton()

        if self.seed_select is not None:
            for option in self.seed_select.options:
                if option.value == self.selected_seed:
                    option.default = True

        elements: list[discord.ui.Item] = [
            self.seed_select,
            self.back_button,
            self.water_button,
            self.plant_button,
            self.harvest_button,
            self.destroy_button,
        ]

        self.clear_items()
        for element in elements:
            if element is not None:
                self.add_item(element)

    async def refresh_ui(self, garden: UserGarden = None):
        if garden is not None:
            self.garden = garden
            self.plot = garden.get_plot(self.x, self.y)
            self.user_seeds = garden.user_seeds

        self.refresh_elements()

        garden_embed = GardenEmbed(self.controller.bot, self.garden)
        content = garden_embed.get_garden_content()
        embed = PlotEmbed(self.plot)

        status_picture = self.plot.get_status_image()
        plot_picture = discord.File(f"./img/garden/{status_picture}", "status.png")

        try:
            await self.message.edit(
                content=content, embed=embed, view=self, attachments=[plot_picture]
            )
        except (discord.NotFound, discord.HTTPException):
            self.controller.detach_view(self)

    async def on_timeout(self):
        with contextlib.suppress(discord.NotFound):
            await self.message.delete()
        self.controller.detach_view(self)


class BackButton(discord.ui.Button):

    def __init__(self):
        super().__init__(label="Back", style=discord.ButtonStyle.grey, row=1)

    async def callback(self, interaction: discord.Interaction):
        view: PlotView = self.view

        if await view.interaction_check(interaction):
            await view.back_to_garden(interaction)


class WaterButton(discord.ui.Button):

    def __init__(self, label: str = "Water"):
        super().__init__(label=label, style=discord.ButtonStyle.blurple, row=1)

    async def callback(self, interaction: discord.Interaction):
        view: PlotView = self.view

        if await view.interaction_check(interaction):
            await view.water(interaction)


class PlantButton(discord.ui.Button):

    def __init__(self, label: str = "Plant"):
        super().__init__(label=label, style=discord.ButtonStyle.green, row=1)

    async def callback(self, interaction: discord.Interaction):
        view: PlotView = self.view

        if await view.interaction_check(interaction):
            await view.plant(interaction)


class HarvestButton(discord.ui.Button):

    def __init__(self, label: str = "Harvest"):
        super().__init__(label=label, style=discord.ButtonStyle.green, row=1)

    async def callback(self, interaction: discord.Interaction):
        view: PlotView = self.view

        if await view.interaction_check(interaction):
            await view.harvest(interaction)


class DestroyButton(discord.ui.Button):

    def __init__(self, label: str = "Remove"):
        super().__init__(label=label, style=discord.ButtonStyle.red, row=1)

    async def callback(self, interaction: discord.Interaction):
        view: PlotView = self.view

        if await view.interaction_check(interaction):
            await view.remove(interaction)


class SeedSelect(discord.ui.Select):

    def __init__(self, bot: commands.Bot, garden: UserGarden):
        options = []

        for plant_type, amount in garden.user_seeds.items():
            plant = garden.get_plant_by_type(plant_type)
            label = plant_type.value + f" ({amount} owned)"
            options.append(
                discord.SelectOption(
                    label=label,
                    value=plant_type,
                    emoji=bot.get_emoji(plant.emoji),
                )
            )

        super().__init__(
            placeholder="Select a seed to plant.",
            min_values=1,
            max_values=1,
            options=options,
            row=0,
        )

    async def callback(self, interaction: discord.Interaction):
        view: PlotView = self.view
        await interaction.response.defer()
        if await view.interaction_check(interaction):
            await view.set_selected_seed(PlantType(self.values[0]))
