from enum import Enum


class UnlockableFeature(str, Enum):
    GARDEN_1 = "Garden 3x1"
    GARDEN_2 = "Garden 3x2"
    GARDEN_3 = "Garden 3x3"
    GARDEN_4 = "Garden 4x3"
    FORGE_SCRAP = "Forge With Scrap"
    FORGE_SHOP = "Forge Shop"
    FORGE_RECIPES = "Forge Recipes"
    ENCHANTMENTS = "Gear Enchantments"
    CRAFTING = "Crafting Enchantments"
    MAX_GAMBA_1 = "Max Gamba Limit and Bonus Beans x2"
    MAX_GAMBA_2 = "Max Gamba Limit and Bonus Beans x4"
    DAILY_BEANS_1 = "Daily Beans Increase x2"
    DAILY_BEANS_2 = "Daily Beans Increase x4"
    DAILY_BEANS_3 = "Daily Beans Increase x8"
    SHOP = "Beans Shop"
    LOTTERY_1 = "Beans Lottery Base Pot x2"
    LOTTERY_2 = "Beans Lottery Base Pot x4"
