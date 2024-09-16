import importlib

from combat.encounter import EncounterContext
from combat.engine.states.state import State
from combat.engine.types import StateType
from control.controller import Controller
from control.types import ControllerModuleMap
from events.bot_event import BotEvent
from events.combat_event import CombatEvent
from events.encounter_event import EncounterEvent
from events.types import CombatEventType, EncounterEventType, EventType


class OpponentTurnState(State):
    def __init__(self, controller: Controller, context: EncounterContext):
        super().__init__(controller, context)
        self.state_type: StateType = StateType.OPPONENT_TURN
        self.next_state: StateType = StateType.TURN_END

    async def startup(self):
        opponent = self.context.opponent

        controller_type = opponent.enemy.controller
        controller_class = getattr(
            importlib.import_module(
                "control.combat.enemy."
                + ControllerModuleMap.get_module(controller_type)
            ),
            controller_type,
        )
        enemy_controller = self.controller.get_service(controller_class)

        await enemy_controller.handle_turn(self.context)
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
            case EventType.COMBAT:
                combat_event: CombatEvent = event
                if combat_event.encounter_id != self.context.encounter.id:
                    return

                if combat_event.combat_event_type in [
                    CombatEventType.ENEMY_TURN,
                    CombatEventType.ENEMY_TURN_STEP,
                ]:
                    await self.skill_manager.trigger_special_skill_effects(event)
                    await self.common.check_actor_defeat(self.context)
                if combat_event.combat_event_type in [
                    CombatEventType.ENEMY_TURN,
                ]:
                    await self.discord.refresh_round_overview(self.context)

    async def update(self):
        pass
