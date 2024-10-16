from enum import Enum


class CombatFeature(str, Enum):
    GARDEN_1 = "Garden 3x1"
    GARDEN_2 = "Garden 3x2"
    GARDEN_3 = "Garden 3x3"
    GARDEN_4 = "Garden 4x3"
    FORGE_SCRAP = "Forge With Scrap"
    FORGE_SHOP = "Forge Shop"
    FORGE_RECIPES = "Forge Recipes"
    ENCHANTMENTS = "Gear Enchantments"
    CRAFTING = "Crafting Enchantments"
    MAX_GAMBA_1 = "Max Gamba limit x2"
    MAX_GAMBA_2 = "Max Gamba limit x4"
    DAILY_BEANS_1 = "Daily Beans Increase x2"
    DAILY_BEANS_2 = "Daily Beans Increase x4"
    DAILY_BEANS_3 = "Daily Beans Increase x8"
    SHOP = "Beans Shop"
