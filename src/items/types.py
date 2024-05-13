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
    PROTECTION = "FartProtection"
    PERM_PROTECTION = "PermProtection"
    ADVANCED_FART_PROTECTION = "AdvancedFartProtection"
    JAIL_REDUCTION = "JailReduction"
    ARREST = "Arrest"
    RELEASE = "Release"
    BAILOUT = "Bailout"
    LOOTBOX = "LootBoxItem"
    LOOTBOX_BUNDLE = "LootBoxItemBundle"
    MIMIC = "PocketMimic"
    LOTTERY_TICKET = "LotteryTicket"
    NAME_COLOR = "NameColor"
    REACTION_SPAM = "ReactionSpam"
    EXPLOSIVE_FART = "ExplosiveFart"
    ROULETTE_FART = "RouletteFart"
    SATAN_FART = "SatanBoost"
    BAT = "Bat"
    CATGIRL = "CatGirl"
    USEFUL_CATGIRL = "UsefulCatGirl"
    UNLIMITED_GAMBA = "NoLimitGamba"
    INSTANT_GAMBA = "NoCooldownGamba"
    CRAPPY_COUPON = "CrappyDrawing"
    PRESTIGE_BEAN = "PrestigeBean"
    PERM_PET_BOOST = "PermPetBoost"
    PERM_SLAP_BOOST = "PermSlapBoost"
    PERM_FART_BOOST = "PermFartBoost"
    ULTRA_BOOST = "UltraBoost"
    INC_PET_BOOST = "IncomingPetBoost"
    MIMIC_DETECTOR = "MimicDetector"

    RARE_SEED = "RareSeed"
    SPEED_SEED = "SpeedSeed"
    BOX_SEED = "BoxSeed"
    CAT_SEED = "CatSeed"
    CRYSTAL_SEED = "CrystalSeed"
    YELLOW_SEED = "YellowSeed"
    GHOST_SEED = "GhostSeed"
    BAKED_SEED = "BakedSeed"


class ItemState(str, Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"


class ItemGroup(str, Enum):
    VALUE_MODIFIER = "value_modifier"
    AUTO_CRIT = "auto_crit"
    BONUS_ATTEMPT = "bonus_attempt"
    STABILIZER = "stabilizer"
    ADVANTAGE = "advantage"
    FLAT_BONUS = "flat_bonus"
    PROTECTION = "protection"
    LOTTERY = "lottery"
    IMMEDIATE_USE = "immediate_use"
    LOOTBOX = "loot_box"
    SUBSCRIPTION = "subscription"
    MAJOR_JAIL_ACTION = "major_jail_action"
    MAJOR_ACTION = "major_action"
    GAMBA = "gamba"
    INCOMING_FLAT_BONUS = "incoming_flat_bonus"
    SEED = "seed"


class ShopCategory(int, Enum):
    LOOTBOX = 0
    FUN = 1
    INTERACTION = 2
    SLAP = 3
    PET = 4
    FART = 5
    JAIL = 6
    GARDEN = 7
