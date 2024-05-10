import contextlib

import discord
from control.controller import Controller
from control.types import ControllerType
from datalayer.garden import UserGarden
from events.types import UIEventType
from events.ui_event import UIEvent
from view.garden.embed import GardenEmbed
from view.view_menu import ViewMenu


class GardenView(ViewMenu):

    def __init__(
        self,
        controller: Controller,
        interaction: discord.Interaction,
        garden: UserGarden,
    ):
        super().__init__(timeout=300)
        self.controller = controller
        self.garden = garden
        self.member_id = interaction.user.id
        self.guild_id = interaction.guild_id
        self.message = None

        self.controller_type = ControllerType.GARDEN_VIEW
        self.controller.register_view(self)
        self.refresh_elements()

    async def listen_for_ui_event(self, event: UIEvent):
        if event.view_id != self.id:
            return

        match event.type:
            case UIEventType.GARDEN_DETACH:
                self.controller.detach_view(self)
                self.stop()

    async def open_plot_view(self, interaction: discord.Interaction, x: int, y: int):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.GARDEN_SELECT_PLOT,
            (interaction, self.garden, x, y, self.message),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    def refresh_elements(self):
        self.clear_items()
        plot_nr = 1

        for plot in self.garden.plots:
            self.add_item(PlotButton(plot.x, plot.y, f"Plot {plot_nr}", plot.empty()))
            plot_nr += 1

    async def refresh_ui(self, garden: UserGarden = None):
        if garden is not None:
            self.garden = garden

        if self.message is None:
            return

        self.refresh_elements()

        author_name = (
            self.controller.bot.get_guild(self.guild_id)
            .get_member(self.controller.bot.user.id)
            .display_name
        )
        profile_picture = discord.File(
            "./img/profile_picture.png", "profile_picture.png"
        )

        embed = GardenEmbed(self.controller.bot, self.garden, author_name)
        try:
            await self.message.edit(
                embed=embed, view=self, attachments=[profile_picture]
            )
        except (discord.NotFound, discord.HTTPException):
            self.controller.detach_view(self)

    async def on_timeout(self):
        with contextlib.suppress(discord.HTTPException):
            await self.message.edit(view=None)
        self.controller.detach_view(self)


class PlotButton(discord.ui.Button):

    def __init__(self, x: int, y: int, label: str, empty: bool = True):
        self.x = x
        self.y = y

        color = discord.ButtonStyle.green if empty else discord.ButtonStyle.grey

        super().__init__(
            label=label,
            style=color,
            row=y,
        )

    async def callback(self, interaction: discord.Interaction):
        view: GardenView = self.view

        if await view.interaction_check(interaction):
            await view.open_plot_view(interaction, self.x, self.y)
