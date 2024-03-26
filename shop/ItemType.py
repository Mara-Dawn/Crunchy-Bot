from enum import Enum

class ItemType(str, Enum):
    AUTO_CRIT = 'AutoCrit'
    FART_BOOST = 'FartBoost'
    PET_BOOST = 'PetBoost'
    SLAP_BOOST = 'SlapBoost'
    BONUS_FART = 'BonusFart'
    BONUS_PET = 'BonusPet'
    BONUS_SLAP = 'BonusSlap'
    GIGA_FART = 'GigaFart'
    FART_STABILIZER = 'FartStabilizer'
    FARTVANTAGE = 'Fartvantage'