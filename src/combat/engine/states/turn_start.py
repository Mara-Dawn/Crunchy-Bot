from combat.actors import Actor
from combat.effects.types import EffectTrigger
from combat.encounter import EncounterContext
from combat.engine.states.state import State
from combat.engine.types import StateType
from control.controller import Controller
from events.bot_event import BotEvent
from events.encounter_event import EncounterEvent
from events.types import EncounterEventType, EventType


class TurnStartState(State):
    def __init__(self, controller: Controller, context: EncounterContext):
        super().__init__(controller, context)
        self.state_type: StateType = StateType.TURN_START
        self.next_state: StateType = None

    async def startup(self):
        await self.discord.refresh_round_overview(self.context)

        actor = self.context.current_actor
        outcome = await self.status_effect_manager.handle_turn_status_effects(
            self.context, actor, EffectTrigger.START_OF_TURN
        )

        self.context.current_turn_embed = self.embed_manager.get_turn_embed(actor)

        if outcome.embed_data is not None:
            await self.discord.update_current_turn_embed(
                self.context, outcome.embed_data
            )
            self.embed_manager.add_spacer_to_embed(self.context.current_turn_embed)

        if self.done:
            # status effects might end encounter early
            self.next_state = StateType.POST_ENCOUNTER
            await self.common.force_end(self.context)
            return

        await self.common.check_actor_defeat(self.context)

        if actor.force_skip:
            await self.skip_turn(actor, self.context)

        elif actor.defeated:
            await self.skip_turn(actor, self.context, f"{actor.name} is defeated.")

        elif actor.leaving:
            await self.skip_turn(
                actor,
                self.context,
                f"{actor.name} has left the encounter and will be removed in the next round.",
            )

        elif actor.is_out:
            await self.skip_turn(actor, self.context, "", silent=True)

        elif actor.is_enemy:
            self.next_state = StateType.OPPONENT_TURN
        else:
            self.next_state = StateType.PLAYER_TURN

        self.done = True

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
                        await self.common.add_member_to_encounter(
                            encounter_event.member_id, self.context
                        )
                    case EncounterEventType.MEMBER_REQUEST_JOIN:
                        await self.common.add_member_join_request(
                            encounter_event.member_id, self.context
                        )
                    case EncounterEventType.END:
                        self.done = True

        return update

    async def update(self):
        pass

    async def skip_turn(
        self,
        actor: Actor,
        context: EncounterContext,
        reason: str = None,
        silent: bool = False,
    ):
        if not silent:
            if reason is None:
                reason = ""
            self.embed_manager.add_turn_skip_to_embed(
                reason, actor, context.current_turn_embed
            )
            await self.discord.update_current_turn_embed(self.context)

        self.next_state = StateType.TURN_END
