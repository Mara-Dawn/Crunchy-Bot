import importlib

from combat.encounter import EncounterContext
from combat.engine.states.state import State
from combat.engine.types import StateType
from control.controller import Controller
from control.types import ControllerModuleMap
from events.bot_event import BotEvent
from events.encounter_event import EncounterEvent
from events.types import EncounterEventType, EventType
from view.combat.leave_view import EncounterLeaveView


class FillingState(State):
    def __init__(self, controller: Controller, context: EncounterContext):
        super().__init__(controller, context)
        self.state_type: StateType = StateType.FILLING
        self.next_state: StateType = StateType.COUNTDOWN

    async def startup(self):
        encounter = self.context.encounter
        thread = self.context.thread
        enemy = await self.factory.get_enemy(encounter.enemy_type)

        wait_embed = await self.embed_manager.get_waiting_for_party_embed(
            self.context.min_participants, self.context.opponent
        )
        leave_view = None
        if not enemy.is_boss:
            leave_view = EncounterLeaveView(self.controller, self.context.encounter.id)
        message = await self.discord.send_message(
            thread, content="", embed=wait_embed, view=leave_view
        )
        if not enemy.is_boss:
            leave_view.set_message(message)

        await self.check_filled()

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
                        await self.check_filled()
                        update = True
                    case EncounterEventType.MEMBER_REQUEST_JOIN:
                        await self.common.add_member_join_request(
                            encounter_event.member_id, self.context
                        )
                    case EncounterEventType.INITIATE:
                        await self.initiate_encounter()
                        update = True
                    case EncounterEventType.MEMBER_DISENGAGE:
                        actor = self.context.get_actor_by_id(event.member_id)
                        if actor is not None:
                            self.context.combatants.remove(actor)
                        await self.check_filled()
                        update = True
                    case EncounterEventType.END:
                        self.next_state = StateType.POST_ENCOUNTER
                        self.done = True
                        await self.common.force_end(self.context)
                        update = True
                    case EncounterEventType.REMOVE_RESTRICTION:
                        await self.check_filled()
                        update = True
        return update

    async def update(self):
        pass

    async def check_filled(self):
        self.logger.log(
            self.context.encounter.guild_id,
            f"({self.context.encounter.id}) filling: {len(self.context.combatants)}/{self.context.min_participants}",
        )
        if len(self.context.combatants) >= self.context.min_participants:
            self.done = True

    async def initiate_encounter(self):
        controller_type = self.context.opponent.enemy.controller
        controller_class = getattr(
            importlib.import_module(
                "control.combat.enemy."
                + ControllerModuleMap.get_module(controller_type)
            ),
            controller_type,
        )
        enemy_controller = self.controller.get_service(controller_class)
        await enemy_controller.intro(self.context.encounter.id)

        for actor in self.context.combatants:
            if (
                not actor.defeated
                and not actor.leaving
                and not actor.is_out
                and actor not in self.context.active_combatants
            ):
                self.context.active_combatants.append(actor)

        self.context._initiated = True
        self.done = True
        self.next_state: StateType = StateType.ROUND_START
