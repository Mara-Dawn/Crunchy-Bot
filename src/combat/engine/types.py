from enum import Enum


class StateType(str, Enum):
    INITIAL = "Initial"
    WAITING = "Waiting"
    FILLING = "Filling"
    COUNTDOWN = "Countdown"
    ROUND_START = "RoundStart"
    ROUND_END = "RoundEnd"
    TURN_START = "TurnStart"
    PLAYER_TURN = "PlayerTurn"
    OPPONENT_TURN = "OpponentTurn"
    TURN_END = "TurnEnd"
    END_SUCCESS = "EndSuccess"
    END_FAILED = "EndFailed"
    LOOT_PAYOUT = "LootPayout"
    POST_ENCOUNTER = "PostEncounter"
