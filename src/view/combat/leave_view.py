import contextlib

import discord

from control.controller import Controller
from control.types import ControllerType
from events.types import UIEventType
from events.ui_event import UIEvent
from view.view_menu import ViewMenu


class EncounterLeaveView(ViewMenu):

    def __init__(self, controller: Controller, encounter_id: int):
        timeout = None
        super().__init__(timeout=timeout)
        self.controller = controller
        self.encounter_id = encounter_id

        self.controller_types = [ControllerType.COMBAT]
        self.controller.register_view(self)

        self.add_item(LeaveButton())

    async def listen_for_ui_event(self, event: UIEvent):
        match event.type:
            case UIEventType.ENCOUNTER_INITIATED:
                encounter_id = event.payload
                if encounter_id == self.encounter_id:
                    await self.on_timeout()

    async def leave(self, interaction: discord.Interaction):
        await interaction.response.defer()

        event = UIEvent(
            UIEventType.COMBAT_LEAVE,
            interaction,
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return True

    async def on_timeout(self):
        with contextlib.suppress(discord.NotFound):
            await self.message.delete()
        self.controller.detach_view(self)


class LeaveButton(discord.ui.Button):

    def __init__(self):
        super().__init__(label="Leave", style=discord.ButtonStyle.red)

    async def callback(self, interaction: discord.Interaction):
        view: EncounterLeaveView = self.view

        await view.leave(interaction)
