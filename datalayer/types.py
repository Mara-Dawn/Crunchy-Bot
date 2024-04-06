from enum import Enum


class UserInteraction(str, Enum):
    SLAP = "slap"
    PET = "pet"
    FART = "fart"


class ItemTrigger(str, Enum):
    SLAP = UserInteraction.SLAP
    PET = UserInteraction.PET
    FART = UserInteraction.FART
    DAILY = "daily"
    USER_MESSAGE = "user_message"
