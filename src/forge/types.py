from enum import Enum


class ForgeableType(str, Enum):
    pass


class IngredientFlag(Enum):
    SAME_FORGE_TYPE = 0
    SAME_OBJECT_TYPE = 1
    SAME_VALUE = 2
    SAME_LEVEL = 3
    SAME_RARITY = 4
    SAME_SLOT = 5


class RecipeType(Enum):
    GEAR_RARITY_UPGRADE = 0
    GEAR_SLOT_REROLL = 1
