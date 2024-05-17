import discord
from control.controller import Controller
from control.types import ControllerType
from events.types import UIEventType
from events.ui_event import UIEvent
from view.view_menu import ViewMenu


class EnemyEngageView(ViewMenu):

    def __init__(self, controller: Controller):
        super().__init__(timeout=None)
        self.controller = controller
        self.add_item(EngageButton())

        self.controller_type = ControllerType.COMBAT
        self.controller.register_view(self)

    async def engage(self, interaction: discord.Interaction):
        await interaction.response.defer()

        event = UIEvent(
            UIEventType.COMBAT_ENGAGE,
            interaction,
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return True

    async def listen_for_ui_event(self, event: UIEvent):
        if event.view_id != self.id:
            return


class EngageButton(discord.ui.Button):

    def __init__(self):
        super().__init__(label="Engage!", style=discord.ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        view: EnemyEngageView = self.view

        await view.engage(interaction)
