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
    SKILL_STACKS = "SkillStacksProxy"
    PHYS_DAMAGE_PROC = "PhysDamageProc"
    MAG_DAMAGE_PROC = "MagDamageProc"
    CLEANSING_HEAL = "CleansingHeal"
    EXTRA_MISSILE = "ExtraMissile"
    BALL_RESET = "BallReset"
    EXTRA_GORE = "ExtraGore"

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
