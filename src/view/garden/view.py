import contextlib
from enum import Enum

import discord
from control.controller import Controller
from control.types import ControllerType
from datalayer.garden import Plot, UserGarden
from datalayer.types import PlotState
from events.types import UIEventType
from events.ui_event import UIEvent
from view.garden.embed import GardenEmbed
from view.view_menu import ViewMenu


class GardenViewState(Enum):
    NORMAL = 0
    WATER = 1


class GardenView(ViewMenu):

    def __init__(
        self,
        controller: Controller,
        interaction: discord.Interaction,
        garden: UserGarden,
    ):
        super().__init__(timeout=None)
        self.controller = controller
        self.garden = garden
        self.member_id = interaction.user.id
        self.guild_id = interaction.guild_id
        self.message = None

        self.state = GardenViewState.NORMAL

        self.controller_types = [ControllerType.GARDEN_VIEW]
        self.controller.register_view(self)
        self.refresh_elements()

    async def listen_for_ui_event(self, event: UIEvent):
        if event.view_id != self.id:
            return

        match event.type:
            case UIEventType.GARDEN_REFRESH:
                garden = event.payload
                await self.refresh_ui(garden)
            case UIEventType.GARDEN_DETACH:
                self.controller.detach_view(self)
                self.stop()

    async def plot_button_clicked(self, interaction: discord.Interaction, plot: Plot):
        await interaction.response.defer()

        match self.state:
            case GardenViewState.NORMAL:
                event = UIEvent(
                    UIEventType.GARDEN_SELECT_PLOT,
                    (interaction, self.garden, plot.x, plot.y, self.message),
                    self.id,
                )
                await self.controller.dispatch_ui_event(event)
            case GardenViewState.WATER:
                event = UIEvent(
                    UIEventType.GARDEN_PLOT_WATER,
                    (interaction, plot),
                    self.id,
                )
                await self.controller.dispatch_ui_event(event)

    async def set_state(
        self, interaction: discord.Interaction, view_state: GardenViewState
    ):
        await interaction.response.defer()
        self.state = view_state
        await self.refresh_ui()

    def refresh_elements(self):
        self.clear_items()
        plot_nr = 1

        for plot in self.garden.plots:
            self.add_item(PlotButton(plot, f"Plot {plot_nr}", self.state))
            plot_nr += 1

        self.add_item(ModeSelectButton(self.state))

    async def refresh_ui(self, garden: UserGarden = None):
        if garden is not None:
            self.garden = garden

        if self.message is None:
            return

        self.refresh_elements()

        embed = GardenEmbed(self.controller.bot, self.garden)
        content = embed.get_garden_content()
        try:
            await self.message.edit(content=content, embed=embed, view=self)
        except (discord.NotFound, discord.HTTPException):
            self.controller.detach_view(self)

    async def on_timeout(self):
        with contextlib.suppress(discord.HTTPException):
            await self.message.edit(view=None)
        self.controller.detach_view(self)


class ModeSelectButton(discord.ui.Button):

    def __init__(self, view_state: GardenViewState):

        match view_state:
            case GardenViewState.NORMAL:
                label = "Enter Water Mode"
                color = discord.ButtonStyle.blurple
                self.click_state = GardenViewState.WATER
            case GardenViewState.WATER:
                label = "Done"
                color = discord.ButtonStyle.grey
                self.click_state = GardenViewState.NORMAL

        super().__init__(
            label=label,
            style=color,
            row=4,
        )

    async def callback(self, interaction: discord.Interaction):
        view: GardenView = self.view

        if await view.interaction_check(interaction):
            await view.set_state(interaction, self.click_state)


class PlotButton(discord.ui.Button):

    def __init__(self, plot: Plot, label: str, view_state: GardenViewState):
        self.plot = plot
        disabled = False

        match plot.get_status():
            case PlotState.EMPTY:
                color = discord.ButtonStyle.grey
                disabled = True
            case PlotState.SEED_PLANTED | PlotState.GROWING:
                color = discord.ButtonStyle.red
            case PlotState.SEED_PLANTED_WET | PlotState.GROWING_WET:
                color = discord.ButtonStyle.blurple
            case PlotState.READY:
                color = discord.ButtonStyle.green
                disabled = True

        if view_state == GardenViewState.NORMAL:
            disabled = False

        super().__init__(label=label, style=color, row=plot.y, disabled=disabled)

    async def callback(self, interaction: discord.Interaction):
        view: GardenView = self.view

        if await view.interaction_check(interaction):
            await view.plot_button_clicked(interaction, self.plot)
