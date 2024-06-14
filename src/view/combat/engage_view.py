import contextlib
import datetime

import discord
from control.controller import Controller
from control.types import ControllerType
from events.types import UIEventType
from events.ui_event import UIEvent
from view.view_menu import ViewMenu


class EnemyEngageView(ViewMenu):

    DEFAULT_TIMEOUT = 60 * 60

    def __init__(self, controller: Controller):
        super().__init__(timeout=self.DEFAULT_TIMEOUT)
        self.controller = controller

        self.controller_type = ControllerType.COMBAT
        self.controller.register_view(self)
        self.encounter_id = None
        self.done = False
        self.active = False
        now = datetime.datetime.now().timestamp()
        self.timeout_timestamp = int(now + self.DEFAULT_TIMEOUT)

        self.refresh_elements()

    async def listen_for_ui_event(self, event: UIEvent):
        match event.type:
            case UIEventType.COMBAT_ENGAGE_UPDATE:
                encounter_id = event.payload[0]
                if encounter_id != self.encounter_id:
                    return
                embed = event.payload[1]
                done = event.payload[2]
                self.active = True
                await self.refresh_ui(embed=embed, done=done)

    async def engage(self, interaction: discord.Interaction):
        await interaction.response.defer()

        event = UIEvent(
            UIEventType.COMBAT_ENGAGE,
            interaction,
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    def refresh_elements(self, disabled: bool = False):
        self.clear_items()
        if not self.done:
            self.add_item(EngageButton())

    async def refresh_ui(
        self,
        embed: discord.Embed,
        encounter_id: int = None,
        done: bool = None,
    ):
        if self.message is None:
            return

        if encounter_id is not None:
            self.encounter_id = encounter_id

        if done is not None and done:
            self.done = done

        self.refresh_elements()

        if self.active and self.timeout is not None:
            self.timeout = None

        if self.done and self.timeout is None:
            self.timeout = self.DEFAULT_TIMEOUT / 5
            now = datetime.datetime.now().timestamp()
            self.timeout_timestamp = int(now + self.DEFAULT_TIMEOUT)

        if not self.active or self.done:
            embed.add_field(
                name=f"Will disappear <t:{self.timeout_timestamp}:R>", value=""
            )

        try:
            await self.message.edit(embed=embed, view=self)
        except (discord.NotFound, discord.HTTPException):
            self.controller.detach_view(self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return True

    async def on_timeout(self):
        with contextlib.suppress(discord.NotFound):
            await self.message.delete()
        self.controller.detach_view(self)


class EngageButton(discord.ui.Button):

    def __init__(self):
        super().__init__(label="Engage!", style=discord.ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        view: EnemyEngageView = self.view

        await view.engage(interaction)
