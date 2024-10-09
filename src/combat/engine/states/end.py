import datetime

from combat.encounter import EncounterContext
from combat.engine.states.state import State
from combat.engine.types import StateType
from control.controller import Controller
from events.bot_event import BotEvent
from events.encounter_event import EncounterEvent
from events.types import EncounterEventType


class EndState(State):
    def __init__(self, controller: Controller, context: EncounterContext):
        super().__init__(controller, context)
        self.state_type: StateType = StateType.ENCOUNTER_END
        self.next_state: StateType = StateType.POST_ENCOUNTER

    async def startup(self):
        await self.discord.delete_previous_combat_info(self.context.thread)

        if self.context.opponent.defeated:
            embed = await self.embed_manager.get_combat_success_embed(self.context)
        else:
            embed = await self.embed_manager.get_combat_failed_embed(self.context)

        await self.discord.send_message(self.context.thread, content="", embed=embed)

        self.context._concluded = True

        event = EncounterEvent(
            datetime.datetime.now(),
            self.context.encounter.guild_id,
            self.context.encounter.id,
            self.bot.user.id,
            EncounterEventType.END,
        )
        await self.controller.dispatch_event(event)

        self.done = True

    async def handle(self, event: BotEvent) -> bool:
        return False

    async def update(self):
        pass
