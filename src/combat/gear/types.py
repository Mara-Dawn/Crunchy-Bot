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
