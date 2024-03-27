from enum import Enum

class ItemGroup(str, Enum):
    VALUE_MODIFIER = 'value_modifier'
    AUTO_CRIT = 'auto_crit'
    BONUS_ATTEMPT = 'bonus_attempt'
    STABILIZER = 'stabilizer'
    ADVANTAGE = 'advantage'
    PROTECTION = 'protection'
    IMMEDIATE_USE = 'immediate_use'