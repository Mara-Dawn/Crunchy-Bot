from enum import Enum

class LootBoxEventType(str, Enum):
    DROP = 'drop'
    CLAIM = 'claim'