from enum import Enum


class UnlockableFeature(str, Enum):
    GARDEN_1 = "**Garden Expansion** 3x1"
    GARDEN_2 = "**Garden Expansion** - Your maximum Garden Plots are expanded to 3x2"
    GARDEN_3 = "**Garden Expansion** - Your maximum Garden Plots are expanded to 3x3"
    GARDEN_4 = "**Garden Expansion** - Your maximum Garden Plots are expanded to 4x3"
    FORGE_SCRAP = (
        "**Forge Scrap** - Throw your Scrap into the forge to gain random items"
    )
    FORGE_SHOP = (
        "**Secret Forge Shop** - Access to totally not Ethel's secret Scrap Shop"
    )
    FORGE_RECIPES = (
        "**Forge Recipes** - Combine any three items in the forge to find all recipes"
    )
    ENCHANTMENTS = "**Gear Enchantments** - Loot powerful Enchantments with special effects to augment your Gear"
    CRAFTING = (
        "**Crafting Enchantments** - Modify your Gear with new crafting Enchantments"
    )
    MAX_GAMBA_1 = "**Max Gamba Limit and Bonus Beans x2**"
    MAX_GAMBA_2 = "**Max Gamba Limit and Bonus Beans x4**"
    DAILY_BEANS_1 = "**Daily Beans Increase x2**"
    DAILY_BEANS_2 = "**Daily Beans Increase x4**"
    DAILY_BEANS_3 = "**Daily Beans Increase x8**"
    SHOP = "**Beans Shop** - Spend your hard earned Beans in Ethel's Beans Shop"
    LOTTERY_1 = "**Beans Lottery Base Pot x2**"
    LOTTERY_2 = "**Beans Lottery Base Pot x4**"
