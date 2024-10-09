from combat.encounter import EncounterContext
from combat.engine.states.state import State
from combat.engine.types import StateType
from control.controller import Controller
from events.bot_event import BotEvent
from events.encounter_event import EncounterEvent
from events.types import EncounterEventType, EventType, UIEventType
from events.ui_event import UIEvent


class WaitingState(State):
    def __init__(self, controller: Controller, context: EncounterContext):
        super().__init__(controller, context)
        self.state_type: StateType = StateType.WAITING
        self.next_state: StateType = StateType.COUNTDOWN

    async def startup(self):
        event = UIEvent(UIEventType.COMBAT_LOADED, self.context.encounter.id)
        await self.controller.dispatch_ui_event(event)

    async def handle(self, event: BotEvent) -> bool:
        update = False
        if not event.synchronized:
            return update
        match event.type:
            case EventType.ENCOUNTER:
                encounter_event: EncounterEvent = event
                if encounter_event.encounter_id != self.context.encounter.id:
                    return update

                match encounter_event.encounter_event_type:
                    case EncounterEventType.MEMBER_ENGAGE:
                        await self.create_encounter_thread(encounter_event.member_id)
                        update = True
                    case EncounterEventType.END:
                        self.next_state = StateType.POST_ENCOUNTER
                        self.done = True
                        update = True
        return update

    async def update(self):
        pass

    async def create_encounter_thread(self, member_id: int):
        encounter = self.context.encounter
        thread = await self.discord.create_encounter_thread(encounter)
        self.context.thread = thread

        if self.context.min_participants > 1:
            self.next_state = StateType.FILLING

        await self.common.add_member_to_encounter(member_id, self.context)

        self.done = True
