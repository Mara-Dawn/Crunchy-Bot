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
    DENIED = "Denied"
    DONE = "Done"
    REFUNDED = "Refunded"


class PredictionStateSort(int, Enum):

    @staticmethod
    def get_prio(prediction_state: PredictionState):
        map = {
            PredictionState.SUBMITTED: 0,
            PredictionState.APPROVED: 1,
            PredictionState.DENIED: 2,
            PredictionState.DONE: 3,
            PredictionState.REFUNDED: 4,
        }

        return map[prediction_state]
