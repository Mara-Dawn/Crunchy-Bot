import discord

from control.controller import Controller
from control.event_manager import EventManager
from control.types import ControllerType
from datalayer.ranking import Ranking
from events.types import UIEventType
from events.ui_event import UIEvent
from view.types import RankingType
from view.view_menu import ViewMenu


class RankingView(ViewMenu):

    def __init__(
        self, controller: Controller, interaction: discord.Interaction, season: int
    ):
        super().__init__(timeout=180)
        self.interaction = interaction
        self.controller = controller
        self.event_manager: EventManager = self.controller.get_service(EventManager)
        self.add_item(Dropdown())
        self.member_id = interaction.user.id
        self.season = season

        self.controller_types = [ControllerType.RANKING_VIEW]
        self.controller.register_view(self)

    async def listen_for_ui_event(self, event: UIEvent):
        if event.view_id != self.id:
            return

    async def edit_page(
        self, interaction: discord.Interaction, ranking_type: RankingType
    ):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.UPDATE_RANKINGS,
            (interaction, ranking_type, self.season),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def on_timeout(self):
        # remove buttons on timeout
        message = await self.interaction.original_response()
        await message.edit(view=None)
        self.controller.detach_view(self)


class Dropdown(discord.ui.Select):

    def __init__(self):
        options = []

        for definition in Ranking.DEFINITIONS.values():
            options.append(
                discord.SelectOption(
                    label=definition.title,
                    description=definition.description,
                    emoji=definition.emoji,
                    value=definition.type,
                )
            )

        super().__init__(
            placeholder="Choose a Leaderbord",
            min_values=1,
            max_values=1,
            options=options,
            row=0,
        )

    async def callback(self, interaction: discord.Interaction):
        view: RankingView = self.view

        if await view.interaction_check(interaction):
            await view.edit_page(interaction, RankingType(int(self.values[0])))
