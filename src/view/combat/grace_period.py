import contextlib

import discord

from combat.encounter import Encounter
from control.controller import Controller
from control.types import ControllerType
from events.types import UIEventType
from events.ui_event import UIEvent
from view.view_menu import ViewMenu


class GracePeriodView(ViewMenu):

    def __init__(
        self,
        controller: Controller,
        encounter: Encounter,
        wait_time: float,
        initial_user: discord.Member | None,
        disable_skip: bool = False,
    ):
        super().__init__(timeout=wait_time)
        self.controller = controller

        self.controller_types = [ControllerType.COMBAT]
        self.controller.register_view(self)
        self.encounter = encounter
        self.initial_user = initial_user

        if not disable_skip:
            self.add_item(SkipButton())

    async def listen_for_ui_event(self, event: UIEvent):
        match event.type:
            case UIEventType.COMBAT_FULL:
                encounter_id = event.payload
                if encounter_id != self.encounter.id:
                    return
                await self.on_timeout()

    async def skip(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.on_timeout()

    async def on_timeout(self):
        with contextlib.suppress(discord.NotFound):
            await self.message.delete()

            event = UIEvent(
                UIEventType.COMBAT_INITIATE,
                self.encounter,
            )
            await self.controller.dispatch_ui_event(event)
        self.controller.detach_view(self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.initial_user.id:
            return True
        else:
            await interaction.response.send_message(
                "Only the encounter initiator may use this.",
                ephemeral=True,
            )
            return False


class SkipButton(discord.ui.Button):

    def __init__(self):
        super().__init__(label="Skip", style=discord.ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        view: GracePeriodView = self.view

        if await view.interaction_check(interaction):
            await view.skip(interaction)
