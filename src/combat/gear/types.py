from enum import Enum

from forge.types import ForgeableType


class EquipmentSlot(str, Enum):
    HEAD = "Head"
    BODY = "Body"
    LEGS = "Bottoms"
    WEAPON = "Weapon"
    ACCESSORY = "Accessory"
    SKILL = "Skill"
    ANY = "Any"
    ARMOR = "Armor"

    @staticmethod
    def is_armor(slot: "EquipmentSlot"):
        return slot in [
            EquipmentSlot.HEAD,
            EquipmentSlot.BODY,
            EquipmentSlot.LEGS,
        ]


class Rarity(str, Enum):
    DEFAULT = "Default"
    COMMON = "Common"
    UNCOMMON = "Uncommon"
    RARE = "Rare"
    LEGENDARY = "Legendary"
    UNIQUE = "Unique"


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
    EVASION = "Evasion"
    DEXTERITY = "Dexterity"
    CONSTITUTION = "Constitution"
    CRANGLED = "Crangled"

    @staticmethod
    def max_name_len():
        max_len = 0
        for name in GearModifierType:
            max_len = max(max_len, len(name.value))
        return max_len

    @staticmethod
    def is_unique_modifier(modifier_type: "GearModifierType"):
        unique_modifiers = [GearModifierType.EVASION]
        return modifier_type in unique_modifiers

    @staticmethod
    def no_value(modifier_type: "GearModifierType"):
        modifiers = [
            GearModifierType.CRANGLED,
        ]
        return modifier_type in modifiers

    @staticmethod
    def short_label(modifier_type: "GearModifierType"):
        label_map = {
            GearModifierType.WEAPON_DAMAGE_MIN: "MIN DMG",
            GearModifierType.WEAPON_DAMAGE_MAX: "MAX DMG",
            GearModifierType.ARMOR: "ARM",
            GearModifierType.DEXTERITY: "DEX",
            GearModifierType.CONSTITUTION: "CON",
            GearModifierType.DEFENSE: "DEF",
            GearModifierType.EVASION: "EVA",
            GearModifierType.ATTACK: "ATK",
            GearModifierType.MAGIC: "MGC",
            GearModifierType.HEALING: "HLG",
            GearModifierType.CRIT_RATE: "CRT %",
            GearModifierType.CRIT_DAMAGE: "CRT DMG",
            GearModifierType.CRANGLED: "CRG",
        }

        return label_map[modifier_type]

    @staticmethod
    def display_value(modifier_type: "GearModifierType", value: float):
        integer_modifiers = [
            GearModifierType.WEAPON_DAMAGE_MIN,
            GearModifierType.WEAPON_DAMAGE_MAX,
            GearModifierType.ARMOR,
            GearModifierType.CONSTITUTION,
            GearModifierType.DEXTERITY,
        ]

        float_modifiers = [
            GearModifierType.DEFENSE,
            GearModifierType.EVASION,
            GearModifierType.ATTACK,
            GearModifierType.MAGIC,
            GearModifierType.HEALING,
            GearModifierType.CRIT_RATE,
            GearModifierType.CRIT_DAMAGE,
        ]

        if modifier_type in integer_modifiers:
            display_value = int(value)
            return f"{display_value}"

        if modifier_type in float_modifiers:
            # display_value = int(value * 10)
            return f"{value:.1f}%"

    @staticmethod
    def prio():
        return [
            GearModifierType.WEAPON_DAMAGE_MIN,
            GearModifierType.WEAPON_DAMAGE_MAX,
            GearModifierType.ARMOR,
            GearModifierType.DEXTERITY,
            GearModifierType.CONSTITUTION,
            GearModifierType.DEFENSE,
            GearModifierType.EVASION,
            GearModifierType.ATTACK,
            GearModifierType.MAGIC,
            GearModifierType.HEALING,
            GearModifierType.CRIT_RATE,
            GearModifierType.CRIT_DAMAGE,
            GearModifierType.CRANGLED,
        ]


class Base(str, Enum):
    GEAR = "Gear"
    SKILL = "Skill"
    ENCHANTMENT = "Enchant"


class GearBaseType(ForgeableType, str, Enum):
    EMPTY = "Empty"

    DEFAULT_PHYS = "DefaultPhys"
    STICK_T0 = "Stick_T0"
    STICK_T1 = "Stick_T1"
    STICK_T2 = "Stick_T2"
    STICK_T3 = "Stick_T3"
    STICK_T4 = "Stick_T4"
    STICK_T5 = "Stick_T5"

    DAGGER = "Dagger"
    ICICLE = "Icicle"
    BLAHAJ = "Blahaj"
    KATANA = "Katana"
    # CHOP_STICKS = "ChopSticks"

    TAPE_MEASURE = "TapeMeasure"
    FROZEN_WAND = "FrozenWand"

    DEFAULT_MAGICAL = "DefaultMagical"
    WAND_T0 = "Wand_T0"
    WAND_T1 = "Wand_T1"
    WAND_T2 = "Wand_T2"
    WAND_T3 = "Wand_T3"
    WAND_T4 = "Wand_T4"
    WAND_T5 = "Wand_T5"

    DEFAULT_HEAD = "DefaultHead"
    HEADGEAR_T0 = "HeadGear_T0"
    HEADGEAR_T1 = "HeadGear_T1"
    HEADGEAR_T2 = "HeadGear_T2"
    HEADGEAR_T2_2 = "HeadGear_T2_2"
    HEADGEAR_T3_1 = "HeadGear_T3_1"
    HEADGEAR_T3_2 = "HeadGear_T3_2"
    HEADGEAR_T4 = "HeadGear_T4"
    HEADGEAR_T5 = "HeadGear_T5"

    DEFAULT_BODY = "DefaultBody"
    BODYGEAR_T0 = "BodyGear_T0"
    BODYGEAR_T1 = "BodyGear_T1"
    BODYGEAR_T2 = "BodyGear_T2"
    BODYGEAR_T3_1 = "BodyGear_T3_1"
    BODYGEAR_T3_2 = "BodyGear_T3_2"
    BODYGEAR_T4 = "BodyGear_T4"
    BODYGEAR_T5 = "BodyGear_T5"

    FEMALE_ARMOR = "FemaleArmor"

    DEFAULT_LEGS = "DefaultLegs"
    LEGGEAR_T0 = "LegGear_T0"
    LEGGEAR_T1 = "LegGear_T1"
    LEGGEAR_T2 = "LegGear_T2"
    LEGGEAR_T3 = "LegGear_T3"
    LEGGEAR_T4 = "LegGear_T4"
    LEGGEAR_T5 = "LegGear_T5"

    HOT_PANTS = "HotPants"

    NECKLACE_T0 = "Necklace_T0"
    RING_T0 = "Ring_T0"
    NECKLACE_T1 = "Necklace_T1"
    NECKLACE_T1_2 = "Necklace_T1_2"
    NECKLACE_T2_1 = "Necklace_T2_1"
    NECKLACE_T2_2 = "Necklace_T2_2"
    NECKLACE_T3_1 = "Necklace_T3_1"
    NECKLACE_T3_2 = "Necklace_T3_2"
    NECKLACE_T4 = "Necklace_T4"
    NECKLACE_T5 = "Necklace_T5"
    NECKLACE_T5_2 = "Necklace_T5_2"

    DEEZ_NUTS = "DeezNutsAccessory"
    RABBIT_FOOT = "RabbitFoot"
    USELESS_AMULET = "UselessAmulet"

    CAT_HEAD = "CatHead"
    CAT_LEGS = "CatLegs"
    CAT_TAIL = "CatTail"
    CAT_HANDS = "CatHands"

    FAST_FOOD_CAP = "FastFoodCap"
    SHOOTER_WIG = "ShooterWig"
    PROFESSIONAL_DISGUISE = "ProfessionalDisguise"

    KEBAB_HAT = "KebabHat"
    KEBAB_APRON = "KebabApron"
    KEBAB_PANTS = "KebabPants"
    KEBAB_SKEWER = "KebabSkewer"


class CharacterAttribute(str, Enum):
    PHYS_DAMAGE_INCREASE = "Physical Damage Inc."
    MAGIC_DAMAGE_INCREASE = "Magical Damage Inc."
    HEALING_BONUS = "Healing Bonus"
    CRIT_RATE = "Crit Rate"
    CRIT_DAMAGE = "Crit Damage"
    DAMAGE_REDUCTION = "Damage Reduction"
    MAX_HEALTH = "Maximum Health"

    @staticmethod
    def max_name_len():
        max_len = 0
        for name in CharacterAttribute:
            max_len = max(max_len, len(name.value))
        return max_len

    @staticmethod
    def display_value(attribute_type: "CharacterAttribute", value: float):
        integer_modifiers = [CharacterAttribute.MAX_HEALTH]

        percentage_modifiers = [
            CharacterAttribute.PHYS_DAMAGE_INCREASE,
            CharacterAttribute.MAGIC_DAMAGE_INCREASE,
            CharacterAttribute.HEALING_BONUS,
            CharacterAttribute.CRIT_RATE,
            CharacterAttribute.CRIT_DAMAGE,
            CharacterAttribute.DAMAGE_REDUCTION,
        ]

        if attribute_type in integer_modifiers:
            return f"{int(value)}"

        if attribute_type in percentage_modifiers:
            percentage = value * 100
            return f"{percentage:.1f}%"
