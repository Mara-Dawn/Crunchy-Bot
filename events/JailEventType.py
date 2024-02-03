from enum import Enum

class JailEventType(str, Enum):
    JAIL = 'jail'
    RELEASE = 'release'
    SLAP = 'slap'
    PET = 'pet'
    FART = 'fart'
    INCREASE = 'increase'
    REDUCE = 'reduce'