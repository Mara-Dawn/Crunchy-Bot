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


class GearModifierType(str, Enum):
    WEAPON_DAMAGE_MIN = "Weapon Min Damage"
    WEAPON_DAMAGE_MAX = "Weapon Max Damage"
    ATTACK = "Attack"
    MAGIC = "Magic"
    CRIT_RATE = "Crit Rate"
    CRIT_DAMAGE = "Crit Damage"
    DEFENSE = "Defense"
    ARMOR = "Armor"
    DEXTERITY = "Dexterity"
    CONSTITUTION = "Constitution"


class CharacterAttribute(str, Enum):
    PHYS_DAMAGE_INCREASE = "Physical Damage Increase"
    MAGIC_DAMAGE_INCREASE = "Magical Damage Increase"
    HEALING_BONUS = "Healing Bonus"
    CRIT_RATE = "Crit Rate"
    CRIT_DAMAGE = "Crit Damage"
    PHYS_DAMAGE_REDUCTION = "Physical Damare Reduction"
    MAGIC_DAMAGE_REDUCTION = "Magical Damage Reduction"
    MAX_HEALTH = "Maximum Health"
