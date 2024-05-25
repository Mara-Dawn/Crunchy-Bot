from enum import Enum


class GearSlot(str, Enum):
    HEAD = "Headpiece"
    BODY = "Body Armor"
    LEGS = "Bottoms"
    WEAPON = "Weapon"
    ACCESSORY = "Accessory"


class GearRarity(str, Enum):
    NORMAL = "Normal"
    MAGIC = "Magic"
    RARE = "Rare"
    LEGENDARY = "Legendary"
    UNIQUE = "Unique"


class EnchantmentType(str, Enum):
    EXAMPLE = "example"


class GearModifierType(str, Enum):
    WEAPON_DAMAGE_MIN = "Min Damage"
    WEAPON_DAMAGE_MAX = "Max Damage"
    ARMOR = "Armor"
    ATTACK = "Attack"
    HEALING = "Healing"
    MAGIC = "Magic"
    CRIT_RATE = "Crit Rate"
    CRIT_DAMAGE = "Crit Damage"
    DEFENSE = "Defense"
    DEXTERITY = "Dexterity"
    CONSTITUTION = "Constitution"

    @staticmethod
    def max_name_len():
        max_len = 0
        for name in GearModifierType:
            max_len = max(max_len, len(name.value))
        return max_len


class GearBaseType(str, Enum):
    EMPTY = "Empty"

    STICK_T0 = "Stick_T0"
    STICK_T1 = "Stick_T1"
    STICK_T2 = "Stick_T2"
    STICK_T3 = "Stick_T3"
    STICK_T4 = "Stick_T4"
    STICK_T5 = "Stick_T5"

    WAND_T0 = "Wand_T0"
    WAND_T1 = "Wand_T1"
    WAND_T2 = "Wand_T2"
    WAND_T3 = "Wand_T3"
    WAND_T4 = "Wand_T4"
    WAND_T5 = "Wand_T5"

    HEADGEAR_T0 = "HeadGear_T0"
    HEADGEAR_T1 = "HeadGear_T1"
    HEADGEAR_T2 = "HeadGear_T2"
    HEADGEAR_T3 = "HeadGear_T3"
    HEADGEAR_T4 = "HeadGear_T4"
    HEADGEAR_T5 = "HeadGear_T5"

    BODYGEAR_T0 = "BodyGear_T0"
    BODYGEAR_T1 = "BodyGear_T1"
    BODYGEAR_T2 = "BodyGear_T2"
    BODYGEAR_T3 = "BodyGear_T3"
    BODYGEAR_T4 = "BodyGear_T4"
    BODYGEAR_T5 = "BodyGear_T5"

    LEGGEAR_T0 = "LegGear_T0"
    LEGGEAR_T1 = "LegGear_T1"
    LEGGEAR_T2 = "LegGear_T2"
    LEGGEAR_T3 = "LegGear_T3"
    LEGGEAR_T4 = "LegGear_T4"
    LEGGEAR_T5 = "LegGear_T5"

    NECKLACE_T0 = "Necklace_T0"
    NECKLACE_T1 = "Necklace_T1"
    NECKLACE_T2 = "Necklace_T2"
    NECKLACE_T3 = "Necklace_T3"
    NECKLACE_T4 = "Necklace_T4"
    NECKLACE_T5 = "Necklace_T5"


class CharacterAttribute(str, Enum):
    PHYS_DAMAGE_INCREASE = "Physical Damage Increase"
    MAGIC_DAMAGE_INCREASE = "Magical Damage Increase"
    HEALING_BONUS = "Healing Bonus"
    CRIT_RATE = "Crit Rate"
    CRIT_DAMAGE = "Crit Damage"
    PHYS_DAMAGE_REDUCTION = "Physical Damare Reduction"
    MAGIC_DAMAGE_REDUCTION = "Magical Damage Reduction"
    MAX_HEALTH = "Maximum Health"

    @staticmethod
    def max_name_len():
        max_len = 0
        for name in CharacterAttribute:
            max_len = max(max_len, len(name.value))
        return max_len
