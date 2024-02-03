from enum import Enum

class RankingType(int, Enum):
    SLAP = 0
    PET= 1
    FART = 2
    SLAP_RECIEVED = 3
    PET_RECIEVED = 4
    FART_RECIEVED = 5
    TIMEOUT_TOTAL = 6
    TIMEOUT_COUNT = 7
    JAIL_TOTAL = 8
    JAIL_COUNT = 9
    SPAM_SCORE = 10