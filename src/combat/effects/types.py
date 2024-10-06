from enum import Enum


class EffectTrigger(Enum):
    START_OF_TURN = 0
    END_OF_TURN = 1
    START_OF_ROUND = 2
    END_OF_ROUND = 3
    ON_DAMAGE_TAKEN = 4
    ON_DEATH = 5
    ON_ATTACK = 7
    POST_ATTACK = 8
    ATTRIBUTE = 9
    ON_SELF_APPLICATION = 10
    END_OF_APPLICANT_TURN = 11
    ON_STATUS_APPLICATION = 12
