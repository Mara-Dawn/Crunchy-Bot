from enum import Enum


class EnchantmentType(str, Enum):
    EMPTY = "Empty"
    CRAFTING = "Crafting"

    # CRAFTING
    CHAOS = "Chaos"
    DIVINE = "Divine"

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
