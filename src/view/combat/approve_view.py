import contextlib

import discord

from combat.encounter import Encounter
from control.controller import Controller
from control.types import ControllerType
from events.types import UIEventType
from events.ui_event import UIEvent
from view.view_menu import ViewMenu


class ApproveMemberView(ViewMenu):

    def __init__(
        self,
        controller: Controller,
        encounter: Encounter,
        joining_member: discord.Member,
        owner: discord.Member,
    ):
        timeout = None
        super().__init__(timeout=timeout)
        self.controller = controller
        self.encounter = encounter
        self.joining_member = joining_member
        self.owner = owner

        self.controller_types = [ControllerType.COMBAT]
        self.controller.register_view(self)

        self.add_item(ApproveButton())

    async def listen_for_ui_event(self, event: UIEvent):
        pass

    async def approve(self, interaction: discord.Interaction):
        await interaction.response.defer()

        event = UIEvent(
            UIEventType.COMBAT_APPROVE,
            (interaction, self.encounter, self.joining_member),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.owner.id:
            return True
        else:
            await interaction.response.send_message(
                "You dont have permission to use this.",
                ephemeral=True,
            )
            return False

    async def on_timeout(self):
        with contextlib.suppress(discord.NotFound):
            await self.message.delete()
        self.controller.detach_view(self)


class ApproveButton(discord.ui.Button):

    def __init__(self):
        super().__init__(label="Approve", style=discord.ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        view: ApproveMemberView = self.view

        if await view.interaction_check(interaction):
            await view.approve(interaction)
