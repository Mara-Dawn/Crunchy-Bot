from combat.encounter import EncounterContext
from combat.engine.states.state import State
from combat.engine.types import StateType
from combat.skills.types import StatusEffectTrigger
from control.controller import Controller
from events.bot_event import BotEvent
from events.encounter_event import EncounterEvent
from events.types import EncounterEventType, EventType


class RoundEndState(State):
    def __init__(self, controller: Controller, context: EncounterContext):
        super().__init__(controller, context)
        self.state_type: StateType = StateType.ROUND_END
        self.next_state: StateType = StateType.ROUND_START

    async def startup(self):
        outcomes = await self.status_effect_manager.handle_round_status_effects(
            self.context, StatusEffectTrigger.END_OF_ROUND
        )

        for actor_id, outcome in outcomes.items():
            if outcome.embed_data is not None:
                status_effect_embed = self.embed_manager.get_status_effect_embed(
                    self.context.get_actor_by_id(actor_id), outcome.embed_data
                )
                await self.discord.append_embed_to_round(
                    self.context, status_effect_embed
                )
        self.done = True

    async def handle(self, event: BotEvent):
        if not event.synchronized:
            return
        match event.type:
            case EventType.ENCOUNTER:
                encounter_event: EncounterEvent = event
                if encounter_event.encounter_id != self.context.encounter.id:
                    return

                match encounter_event.encounter_event_type:
                    case EncounterEventType.MEMBER_ENGAGE:
                        await self.common.add_member_to_encounter(
                            encounter_event.member_id, self.context
                        )
                    case EncounterEventType.MEMBER_REQUEST_JOIN:
                        await self.common.add_member_join_request(
                            encounter_event.member_id, self.context
                        )

    async def update(self):
        pass
