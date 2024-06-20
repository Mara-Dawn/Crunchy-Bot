from enum import Enum


class EmojiType(str, Enum):
    DEFAULT = "default"
    CUSTOM = "custom"


class RankingType(int, Enum):
    SLAP = 0
    PET = 1
    FART = 2
    SLAP_RECIEVED = 3
    PET_RECIEVED = 4
    FART_RECIEVED = 5
    TIMEOUT_TOTAL = 6
    TIMEOUT_COUNT = 7
    JAIL_TOTAL = 8
    JAIL_COUNT = 9
    SPAM_SCORE = 10
    BEANS = 11
    MIMICS = 12
    TOTAL_GAMBAD_SPENT = 13
    TOTAL_GAMBAD_WON = 14
    BEANS_CURRENT = 15
    WIN_RATE = 16
    AVG_GAMBA_GAIN = 17
    WIN_STREAK = 18
    LOSS_STREAK = 19
    KARMA = 20
    GOLD_STARS = 21
    FUCK_YOUS = 22


class ActionType(str, Enum):
    ENABLE_ACTION = "Enable"
    DISABLE_ACTION = "Disable"
    DEFAULT_ACTION = "Action"
    USE_ACTION = "Use"
