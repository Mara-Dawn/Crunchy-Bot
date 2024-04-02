from enum import Enum

class ItemGroup(str, Enum):
    VALUE_MODIFIER = 'value_modifier'
    AUTO_CRIT = 'auto_crit'
    BONUS_ATTEMPT = 'bonus_attempt'
    STABILIZER = 'stabilizer'
    ADVANTAGE = 'advantage'
    PROTECTION = 'protection'
    LOTTERY = 'lottery'
    IMMEDIATE_USE = 'immediate_use'
    LOOTBOX = 'loot_box'
    DAILY_USE = 'daily_use'