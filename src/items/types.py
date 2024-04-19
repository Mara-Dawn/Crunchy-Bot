from enum import Enum


class ItemType(str, Enum):
    AUTO_CRIT = "AutoCrit"
    FART_BOOST = "FartBoost"
    PET_BOOST = "PetBoost"
    SLAP_BOOST = "SlapBoost"
    BONUS_FART = "BonusFart"
    BONUS_PET = "BonusPet"
    BONUS_SLAP = "BonusSlap"
    GIGA_FART = "GigaFart"
    FART_STABILIZER = "FartStabilizer"
    FARTVANTAGE = "Fartvantage"
    FART_PROTECTION = "FartProtection"
    JAIL_REDUCTION = "JailReduction"
    ARREST = "Arrest"
    RELEASE = "Release"
    BAILOUT = "Bailout"
    LOOTBOX = "LootBoxItem"
    LOTTERY_TICKET = "LotteryTicket"
    NAME_COLOR = "NameColor"
    REACTION_SPAM = "ReactionSpam"
    EXPLOSIVE_FART = "ExplosiveFart"
    ROULETTE_FART = "RouletteFart"
    SATAN_FART = "SatanBoost"
    BAT = "Bat"
    PREDICTION_SUBMISSION = "PredictionSubmission"


class ItemGroup(str, Enum):
    VALUE_MODIFIER = "value_modifier"
    AUTO_CRIT = "auto_crit"
    BONUS_ATTEMPT = "bonus_attempt"
    STABILIZER = "stabilizer"
    ADVANTAGE = "advantage"
    PROTECTION = "protection"
    LOTTERY = "lottery"
    IMMEDIATE_USE = "immediate_use"
    LOOTBOX = "loot_box"
    SUBSCRIPTION = "subscription"


class ShopCategory(int, Enum):
    FUN = 0
    INTERACTION = 1
    SLAP = 2
    PET = 3
    FART = 4
    JAIL = 5
