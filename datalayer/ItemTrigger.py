from enum import Enum

from datalayer.UserInteraction import UserInteraction

class ItemTrigger(str, Enum):
    SLAP = UserInteraction.SLAP
    PET = UserInteraction.PET
    FART = UserInteraction.FART
    DAILY = 'daily'
    USER_MESSAGE = 'user_message'