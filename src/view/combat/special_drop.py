import asyncio
import contextlib

import discord
from control.combat.combat_embed_manager import CombatEmbedManager
from control.controller import Controller
from control.types import ControllerType
from events.types import UIEventType
from events.ui_event import UIEvent
from items.item import Item
from view.view_menu import ViewMenu


class SpecialDropView(ViewMenu):

    def __init__(
        self,
        controller: Controller,
        encounter_id: int,
        item: Item,
        delay: float = None,
    ):
        super().__init__(timeout=None)
        self.controller = controller

        self.encounter_id = encounter_id
        self.item = item

        self.blocked = False
        self.embed_manager: CombatEmbedManager = self.controller.get_service(
            CombatEmbedManager
        )

        self.controller_types = [ControllerType.COMBAT]
        self.controller.register_view(self)

        if delay is not None:
            self.refresh_elements(disabled=True)
            self.delay_task = asyncio.create_task(self.unlock_task(delay))
        else:
            self.refresh_elements(disabled=False)

    def refresh_elements(self, disabled: bool):
        self.clear_items()
        self.add_item(ClaimButton(disabled=disabled))

    async def unlock_task(self, delay: float = None):
        if delay is None:
            return

        await asyncio.sleep(delay)
        self.refresh_elements(disabled=False)
        with contextlib.suppress(discord.NotFound):
            embed = self.embed_manager.get_special_item_embed(self.item)
            await self.message.edit(embed=embed, view=self)

    async def claim(self, interaction: discord.Interaction):
        await interaction.response.defer()

        if self.blocked:
            return

        event = UIEvent(
            UIEventType.CLAIM_SPECIAL_DROP,
            (interaction, self.encounter_id, self.item),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return True

    async def listen_for_ui_event(self, event: UIEvent):
        if event.view_id != self.id:
            return
        match event.type:
            case UIEventType.STOP_INTERACTIONS:
                self.blocked = True
            case UIEventType.RESUME_INTERACTIONS:
                self.blocked = False

    async def on_timeout(self):
        self.timeout = None
        self.refresh_elements()
        with contextlib.suppress(discord.NotFound):
            embed = self.embed_manager.get_special_item_embed(self.item)
            await self.message.edit(embed=embed, view=self)


class ClaimButton(discord.ui.Button):

    def __init__(self, disabled: bool = True):
        super().__init__(
            label="Claim", style=discord.ButtonStyle.green, disabled=disabled
        )

    async def callback(self, interaction: discord.Interaction):
        view: SpecialDropView = self.view

        await view.claim(interaction)
