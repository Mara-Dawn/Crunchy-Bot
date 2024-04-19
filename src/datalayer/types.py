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


class PredictionState(str, Enum):
    SUBMITTED = "Submitted"
    APPROVED = "Approved"
    LOCKED = "Locked"
    DENIED = "Denied"
    DONE = "Done"
    REFUNDED = "Refunded"


class PredictionStateSort(int, Enum):

    @staticmethod
    def get_prio(prediction_state: PredictionState):
        map = {
            PredictionState.SUBMITTED: 0,
            PredictionState.APPROVED: 1,
            PredictionState.LOCKED: 2,
            PredictionState.DENIED: 3,
            PredictionState.DONE: 4,
            PredictionState.REFUNDED: 5,
        }

        return map[prediction_state]