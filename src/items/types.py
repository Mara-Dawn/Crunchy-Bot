from enum import Enum

from forge.types import ForgeableType


class ItemType(ForgeableType, str, Enum):
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
    LOOTBOX_BIG_BUNDLE = "LootBoxItemBigBundle"
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
    BETA_BADGE = "BetaBadge"
    PERM_PET_BOOST = "PermPetBoost"
    PERM_SLAP_BOOST = "PermSlapBoost"
    PERM_FART_BOOST = "PermFartBoost"
    ULTRA_BOOST = "UltraBoost"
    INC_PET_BOOST = "IncomingPetBoost"
    MIMIC_DETECTOR = "MimicDetector"
    SPOOK_BEAN = "GhostBean"

    CHEST_BEANS = "ChestBeansReward"
    CHEST_MIMIC = "ChestMimic"
    CHEST_LARGE_MIMIC = "ChestLargeMimic"
    CHEST_SPOOK_MIMIC = "ChestSpookMimic"

    HIGH_AS_FRICK = "HighAsFrick"
    EGIRL_DEBUFF = "UwUfy"
    RELIGION_DEBUFF = "Religify"
    ALCOHOL_DEBUFF = "Alcoholify"
    WEEB_DEBUFF = "Weebify"
    BRIT_DEBUFF = "Britify"
    MEOW_DEBUFF = "Meowify"
    NERD_DEBUFF = "Nerdify"
    TRUMP_DEBUFF = "Trumpify"
    MACHO_DEBUFF = "Machofy"

    BEAN_SEED = "BaseSeed"
    RARE_SEED = "RareSeed"
    SPEED_SEED = "SpeedSeed"
    BOX_SEED = "BoxSeed"
    CAT_SEED = "CatSeed"
    CRYSTAL_SEED = "CrystalSeed"
    YELLOW_SEED = "YellowSeed"
    GHOST_SEED = "GhostSeed"
    BAKED_SEED = "BakedSeed"
    FLASH_SEED = "FlashSeed"
    KEY_SEED = "KeySeed"

    SCRAP = "Scrap"

    ENCOUNTER_KEY = "BaseKey"
    ENCOUNTER_KEY_1 = "KeyLvl1"
    ENCOUNTER_KEY_2 = "KeyLvl2"
    ENCOUNTER_KEY_3 = "KeyLvl3"
    ENCOUNTER_KEY_4 = "KeyLvl4"
    ENCOUNTER_KEY_5 = "KeyLvl5"
    ENCOUNTER_KEY_6 = "KeyLvl6"
    ENCOUNTER_KEY_7 = "KeyLvl7"

    DADDY_KEY = "DaddyKey"
    WEEB_KEY = "WeebKey"


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
    DEBUFF = "debuff"
    GEAR = "gear"
    MISC = "misc"


class ShopCategory(int, Enum):
    LOOTBOX = 0
    FUN = 1
    INTERACTION = 2
    SLAP = 3
    PET = 4
    FART = 5
    JAIL = 6
    GARDEN = 7
    GEAR = 8
