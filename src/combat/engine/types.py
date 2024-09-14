from enum import Enum


class EncounterState(str, Enum):
    INITIAL = "Initial"
    FILLING = "Filling"
    COUNTDOWN = "Countdown"
    NEW_ROUND = "NewRound"
    NEW_TURN = "NewTurn"
    PLAYER_TURN = "PlayerTurn"
    OPPONENT_TURN = "OpponentTurn"
    END = "End"
    LOOT_PAYOUT = "LootPayout"
    POST_END = "PostEnd"
