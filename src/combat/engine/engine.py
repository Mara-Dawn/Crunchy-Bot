from collections.abc import Callable

from combat.encounter import EncounterContext
from combat.engine.common import CommonService
from combat.engine.states.countdown import CountdownState
from combat.engine.states.end_failed import EndFailedState
from combat.engine.states.end_success import EndSuccessState
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


class Engine:
    def __init__(self, controller: Controller, context: EncounterContext):
        self.controller = controller
        self.states: dict[StateType:Callable] = {
            StateType.INITIAL: InitialState,
            StateType.WAITING: WaitingState,
            StateType.FILLING: FillingState,
            StateType.COUNTDOWN: CountdownState,
            StateType.ROUND_START: RoundStartState,
            StateType.ROUND_END: RoundEndState,
            StateType.TURN_START: TurnStartState,
            StateType.PLAYER_TURN: PlayerTurn,
            StateType.OPPONENT_TURN: OpponentTurnState,
            StateType.TURN_END: TurnEndState,
            StateType.END_SUCCESS: EndSuccessState,
            StateType.END_FAILED: EndFailedState,
            StateType.LOOT_PAYOUT: LootPayoutState,
            StateType.POST_ENCOUNTER: PostEncounterState,
        }
        self.done = False
        self.current_state: StateType = StateType.INITIAL
        self.state: State = self.states[self.current_state](controller, context)
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
        self.state = self.states[self.current_state](self.controller, self.context)
        await self.state.startup()
        if self.state.quit:
            self.done = True
        elif self.state.done:
            await self.state_transition()

    async def update(self):
        if self.context.initiated:
            await self.discord.refresh_round_overview(self.context)
            enemy_embed = await self.embed_manager.get_combat_embed(self.context)
            message = await self.discord.get_previous_enemy_info(self.context.thread)
            if message is not None:
                await self.discord.edit_message(message, embed=enemy_embed)

        await self.common.check_actor_defeat(self.context)
        if self.context.concluded:
            return

        if self.context.opponent.defeated:
            await self.discord.delete_previous_combat_info(self.context.thread)
            self.state.done = True
            self.state.next_state = StateType.END_SUCCESS

        if self.context.initiated and len(self.context.active_combatants) <= 0:
            await self.discord.delete_previous_combat_info(self.context.thread)
            self.state.done = True
            self.state.next_state = StateType.END_FAILED

        if self.state.quit:
            self.done = True
        elif self.state.done:
            await self.state_transition()
        await self.state.update()

    async def handle(self, event: BotEvent):
        if not self.done:
            if (
                self.context.encounter is None
                or event.encounter_id != self.context.encounter.id
            ):
                return

            message = f"({self.context.encounter.id}) Handling {event.type.value} event in state {self.state.state_type.value}"
            self.logger.log(self.context.encounter.guild_id, message, self.log_name)

            await self.state.handle(event)
            await self.update()

    async def run(self):
        message = "Initializing combat engine"
        self.logger.log(self.context.encounter.guild_id, message, self.log_name)
        await self.state.startup()
        if self.state.quit:
            self.done = True
        elif self.state.done:
            await self.state_transition()
