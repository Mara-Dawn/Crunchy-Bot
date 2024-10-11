import datetime
from collections.abc import Callable

from combat.encounter import EncounterContext
from combat.engine.common import CommonService
from combat.engine.states.countdown import CountdownState
from combat.engine.states.end import EndState
from combat.engine.states.filling import FillingState
from combat.engine.states.initial import InitialState
from combat.engine.states.loot import LootPayoutState
from combat.engine.states.opponent_turn import OpponentTurnState
from combat.engine.states.player_turn import PlayerTurn
from combat.engine.states.post_encounter import PostEncounterState
from combat.engine.states.round_end import RoundEndState
from combat.engine.states.round_start import RoundStartState
from combat.engine.states.state import State
from combat.engine.states.turn_end import TurnEndState
from combat.engine.states.turn_start import TurnStartState
from combat.engine.states.waiting import WaitingState
from combat.engine.types import StateType
from control.combat.combat_embed_manager import CombatEmbedManager
from control.combat.discord_manager import DiscordManager
from control.controller import Controller
from events.bot_event import BotEvent
from events.encounter_event import EncounterEvent
from events.types import EncounterEventType


class Engine:

    def __init__(self, controller: Controller, context: EncounterContext):
        self.controller = controller
        self.bot = self.controller.bot
        self.state_init: list[Callable] = {
            InitialState,
            WaitingState,
            FillingState,
            CountdownState,
            RoundStartState,
            RoundEndState,
            TurnStartState,
            PlayerTurn,
            OpponentTurnState,
            TurnEndState,
            LootPayoutState,
            EndState,
            PostEncounterState,
        }

        self.states: dict[StateType:Callable] = {}

        for element in self.state_init:
            state: State = element(controller, context)
            self.states[state.state_type] = state

        self.done = False
        self.current_state: StateType = StateType.INITIAL
        self.state: State = self.states[self.current_state]
        self.context = context
        self.common: CommonService = self.controller.get_service(CommonService)
        self.discord: DiscordManager = self.controller.get_service(DiscordManager)
        self.embed_manager: CombatEmbedManager = self.controller.get_service(
            CombatEmbedManager
        )
        self.logger = self.controller.logger
        self.log_name = "Combat Engine"

    async def state_transition(self):
        message = f"({self.context.encounter.id}) Transition: {self.state.state_type.value} -> {self.state.next_state.value}"
        self.logger.log(self.context.encounter.guild_id, message, self.log_name)

        next_state = self.state.next_state
        self.state.done = False
        self.current_state = next_state
        self.state = self.states[self.current_state]
        await self.state.startup()
        if self.state.done:
            await self.update()
        elif self.state.quit:
            await self.end()

    async def update(self):
        if self.done:
            return

        if self.context.initiated:
            await self.common.check_actor_defeat(self.context)

            if self.current_state not in [
                StateType.ENCOUNTER_END,
                StateType.LOOT_PAYOUT,
                StateType.POST_ENCOUNTER,
            ] and (
                self.context.opponent.defeated
                or len(self.context.active_combatants) <= 0
            ):
                self.state.done = True
                self.state.next_state = StateType.ENCOUNTER_END

        if self.state.quit:
            await self.end()
        elif self.state.done:
            await self.state_transition()
        else:
            await self.state.update()

    async def end(self):
        self.done = True
        event = EncounterEvent(
            datetime.datetime.now(),
            self.context.encounter.guild_id,
            self.context.encounter.id,
            self.bot.user.id,
            EncounterEventType.CLEANUP,
        )
        await self.controller.dispatch_event(event)

    async def handle(self, event: BotEvent):
        if not self.done:
            if self.context.encounter is None:
                return

            if await self.state.handle(event):
                await self.update()

    async def run(self):
        await self.state.startup()
        if self.state.quit:
            self.done = True
        elif self.state.done:
            await self.update()
