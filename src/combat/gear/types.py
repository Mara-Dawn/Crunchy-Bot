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
    WEAPON_DAMAGE_MIN = "Weapon Min Damage"
    WEAPON_DAMAGE_MAX = "Weapon Max Damage"
    ARMOR = "Armor"
    ATTACK = "Attack"
    HEALING = "Healing"
    MAGIC = "Magic"
    CRIT_RATE = "Crit Rate"
    CRIT_DAMAGE = "Crit Damage"
    DEFENSE = "Defense"
    DEXTERITY = "Dexterity"
    CONSTITUTION = "Constitution"


class GearBaseType(str, Enum):
    STICK_T0 = "Stick_T0"
    WAND_T0 = "Wand_T0"

    HEADGEAR_T0 = "HeadGear_T0"

    BODYGEAR_T0 = "BodyGear_T0"

    LEGGEAR_T0 = "LegGear_T0"

    NECKLACE_T0 = "Necklace_T0"


class CharacterAttribute(str, Enum):
    PHYS_DAMAGE_INCREASE = "Physical Damage Increase"
    MAGIC_DAMAGE_INCREASE = "Magical Damage Increase"
    HEALING_BONUS = "Healing Bonus"
    CRIT_RATE = "Crit Rate"
    CRIT_DAMAGE = "Crit Damage"
    PHYS_DAMAGE_REDUCTION = "Physical Damare Reduction"
    MAGIC_DAMAGE_REDUCTION = "Magical Damage Reduction"
    MAX_HEALTH = "Maximum Health"
