from combat.encounter import EncounterContext
from combat.engine.states.state import State
from combat.engine.types import StateType
from config import Config
from control.controller import Controller
from events.bot_event import BotEvent
from events.encounter_event import EncounterEvent
from events.types import EncounterEventType, EventType


class WaitingState(State):
    def __init__(self, controller: Controller, context: EncounterContext):
        super().__init__(controller, context)
        self.state_type: StateType = StateType.WAITING
        self.next_state: StateType = StateType.COUNTDOWN

    async def startup(self):
        pass

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
                        await self.create_encounter_thread(encounter_event.member_id)

    async def update(self):
        pass

    async def create_encounter_thread(self, member_id: int):
        encounter = self.context.encounter
        thread = await self.discord.create_encounter_thread(encounter)
        self.context.thread = thread

        enemy = await self.factory.get_enemy(encounter.enemy_type)

        min_participants = enemy.min_encounter_scale
        guild_level = await self.database.get_guild_level(encounter.guild_id)

        if encounter.enemy_level == guild_level:
            min_participants = max(
                min_participants,
                int(enemy.max_players * Config.ENCOUNTER_MAX_LVL_SIZE_SCALING),
            )

        if min_participants > 1:
            self.next_state = StateType.FILLING

        await self.common.add_member_to_encounter(member_id, self.context)

        self.done = True
