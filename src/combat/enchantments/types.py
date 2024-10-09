from enum import Enum


class EnchantmentType(str, Enum):
    EMPTY = "Empty"
    CRAFTING = "Crafting"

    # CRAFTING
    CHAOS = "Chaos"
    DIVINE = "Divine"
    EXALTED = "Exalted"
    CHANCE = "Chance"
    CRANGLE = "Crangle"

    # ENCHANTMENTS
    DEATH_SAVE = "DeathSave"

    # Player Skills
    # Physical

    @staticmethod
    def adds_enchantment(enchantment_type: "EnchantmentType"):
        return enchantment_type in [
            EnchantmentType.DEATH_SAVE,
        ]

    @staticmethod
    def is_crafting(enchantment_type: "EnchantmentType"):
        return enchantment_type in [
            EnchantmentType.CHAOS,
        ]


class EnchantmentEffect(str, Enum):
    EFFECT = "Effect"
    CRAFTING = "Crafting"


class EnchantmentFilterFlags(Enum):
    MATCH_RARITY = 1
    LESS_OR_EQUAL_RARITY = 2
    MATCH_COMMON_RARITY = 3
