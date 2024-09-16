import datetime

from combat.encounter import EncounterContext
from combat.engine.states.state import State
from combat.engine.types import StateType
from combat.skills.types import StatusEffectTrigger
from control.controller import Controller
from events.bot_event import BotEvent
from events.encounter_event import EncounterEvent
from events.types import EncounterEventType, EventType
from view.combat.leave_view import EncounterLeaveView


class RoundStartState(State):
    def __init__(self, controller: Controller, context: EncounterContext):
        super().__init__(controller, context)
        self.state_type: StateType = StateType.ROUND_START
        self.next_state: StateType = StateType.TURN_START

    async def startup(self):
        outcomes = await self.status_effect_manager.handle_round_status_effects(
            self.context, StatusEffectTrigger.START_OF_ROUND
        )

        for actor_id, outcome in outcomes.items():
            if outcome.embed_data is not None:
                status_effect_embed = self.embed_manager.get_status_effect_embed(
                    self.context.get_actor_by_id(actor_id), outcome.embed_data
                )
                await self.discord.append_embed_to_round(
                    self.context, status_effect_embed
                )

        for actor in self.context.initiative:
            actor.round_modifier = (
                await self.status_effect_manager.handle_attribute_status_effects(
                    self.context, actor
                )
            )

            if actor.leaving:
                event = EncounterEvent(
                    datetime.datetime.now(),
                    self.context.encounter.guild_id,
                    self.context.encounter.id,
                    actor.id,
                    EncounterEventType.MEMBER_OUT,
                )
                await self.controller.dispatch_event(event)

                if actor in self.context.active_combatants:
                    self.context.active_combatants.remove(actor)

        await self.common.check_actor_defeat(self.context)

        encounter = self.context.encounter
        thread = self.context.thread
        self.context.round_number += 1
        self.context._current_actor = None
        for actor in self.context.combatants:
            if (
                not actor.defeated
                and not actor.leaving
                and not actor.is_out
                and actor not in self.context.active_combatants
            ):
                self.context.active_combatants.append(actor)

        self.context.refresh_initiative(reset=True)

        event = EncounterEvent(
            datetime.datetime.now(),
            self.context.encounter.guild_id,
            self.context.encounter.id,
            self.bot.user.id,
            EncounterEventType.NEW_ROUND,
        )
        await self.controller.dispatch_event(event)

        enemy_embed = await self.embed_manager.get_combat_embed(self.context)

        await self.discord.delete_previous_combat_info(thread)
        leave_view = None
        if not self.context.opponent.enemy.is_boss:
            leave_view = EncounterLeaveView(self.controller, encounter.id)
        message = await self.discord.send_message(
            thread, content="", embed=enemy_embed, view=leave_view
        )
        if not self.context.opponent.enemy.is_boss:
            leave_view.set_message(message)
        round_embed = await self.embed_manager.get_round_embed(self.context)
        await self.discord.send_message(thread, content="", embed=round_embed)

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
                    case EncounterEventType.NEW_ROUND:
                        self.context._round_event_id_cutoff = event.id

    async def update(self):
        pass
