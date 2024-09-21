import datetime
import importlib

from combat.encounter import EncounterContext
from combat.engine.states.state import State
from combat.engine.types import StateType
from config import Config
from control.controller import Controller
from control.types import ControllerModuleMap
from events.bot_event import BotEvent
from events.encounter_event import EncounterEvent
from events.types import EncounterEventType, EventType
from view.combat.grace_period import GracePeriodView


class CountdownState(State):
    def __init__(self, controller: Controller, context: EncounterContext):
        super().__init__(controller, context)
        self.state_type: StateType = StateType.COUNTDOWN
        self.next_state: StateType = StateType.ROUND_START

    async def startup(self):
        encounter = self.context.encounter
        thread = self.context.thread
        wait_time = Config.COMBAT_INITIAL_WAIT
        round_embed = await self.embed_manager.get_initiation_embed(
            wait_time, self.context.opponent
        )
        # will trigger the combat start on expiration
        view = GracePeriodView(self.controller, encounter, wait_time)
        message = await self.discord.send_message(
            thread, content="", embed=round_embed, view=view
        )
        view.set_message(message)

        # event = EncounterEvent(
        #     datetime.datetime.now(),
        #     encounter.guild_id,
        #     encounter.id,
        #     838500543546523678,
        #     EncounterEventType.MEMBER_ENGAGE,
        # )
        # await self.controller.dispatch_event(event)

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
                    case EncounterEventType.INITIATE:
                        await self.initiate_encounter()
                        update = True
                    case EncounterEventType.MEMBER_ENGAGE:
                        await self.common.add_member_to_encounter(
                            encounter_event.member_id, self.context
                        )
                    case EncounterEventType.MEMBER_REQUEST_JOIN:
                        await self.common.add_member_join_request(
                            encounter_event.member_id, self.context
                        )
                    case EncounterEventType.MEMBER_DISENGAGE:
                        actor = self.context.get_actor_by_id(event.member_id)
                        if actor is not None:
                            self.context.combatants.remove(actor)
                        update = True

        return update

    async def update(self):
        pass

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
