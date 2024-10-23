import contextlib

import discord

from combat.encounter import Encounter
from control.controller import Controller
from control.types import ControllerType
from events.types import UIEventType
from events.ui_event import UIEvent
from view.view_menu import ViewMenu


class GracePeriodView(ViewMenu):

    def __init__(self, controller: Controller, encounter: Encounter, wait_time: float):
        super().__init__(timeout=wait_time)
        self.controller = controller

        self.controller_types = [ControllerType.COMBAT]
        self.controller.register_view(self)
        self.encounter = encounter

    async def listen_for_ui_event(self, event: UIEvent):
        match event.type:
            case UIEventType.COMBAT_FULL:
                encounter_id = event.payload
                if encounter_id != self.encounter.id:
                    return
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
