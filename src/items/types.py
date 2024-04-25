from enum import Enum


class ItemType(str, Enum):
    AUTO_CRIT = "AutoCrit"
    FART_BOOST = "FartBoost"
    ULTRA_FART_BOOST = "UltraFartBoost"
    PET_BOOST = "PetBoost"
    SLAP_BOOST = "SlapBoost"
    BONUS_FART = "BonusFart"
    BONUS_PET = "BonusPet"
    ULTRA_PET = "UltraPet"
    PENETRATING_PET = "PenetratingPet"
    BONUS_SLAP = "BonusSlap"
    ULTRA_SLAP = "UltraSlap"
    SWAP_SLAP = "SwapSlap"
    GIGA_FART = "GigaFart"
    FART_STABILIZER = "FartStabilizer"
    FARTVANTAGE = "Fartvantage"
    FART_PROTECTION = "FartProtection"
    ADVANCED_FART_PROTECTION = "AdvancedFartProtection"
    JAIL_REDUCTION = "JailReduction"
    ARREST = "Arrest"
    RELEASE = "Release"
    BAILOUT = "Bailout"
    LOOTBOX = "LootBoxItem"
    LOOTBOX_BUNDLE = "LootBoxItemBundle"
    LOTTERY_TICKET = "LotteryTicket"
    NAME_COLOR = "NameColor"
    REACTION_SPAM = "ReactionSpam"
    EXPLOSIVE_FART = "ExplosiveFart"
    ROULETTE_FART = "RouletteFart"
    SATAN_FART = "SatanBoost"
    BAT = "Bat"
    PREDICTION_SUBMISSION = "PredictionSubmission"


class ItemState(str, Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"


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
    MAJOR_JAIL_ACTION = "major_jail_action"
    MAJOR_ACTION = "major_action"


class ShopCategory(int, Enum):
    LOOTBOX = 0
    FUN = 1
    INTERACTION = 2
    SLAP = 3
    PET = 4
    FART = 5
    JAIL = 6
