from combat.gear.bases import (
    BodyGear_T0,
    Empty,
    HeadGear_T0,
    LegGear_T0,
    Stick_T0,
    Wand_T0,
)
from combat.gear.gear import Gear
from combat.gear.types import GearModifierType, GearRarity

# Starting Gear


class DefaultStick(Gear):

    def __init__(self):

        super().__init__(
            name="Stick",
            base=Stick_T0(),
            rarity=GearRarity.NORMAL,
            level=1,
            modifiers={
                GearModifierType.WEAPON_DAMAGE_MIN: 1,
                GearModifierType.WEAPON_DAMAGE_MAX: 2,
            },
            skills=[],
            enchantments=[],
            id=-1,
        )


class DefaultWand(Gear):

    def __init__(self):

        super().__init__(
            name="Wand",
            base=Wand_T0(),
            rarity=GearRarity.NORMAL,
            level=1,
            modifiers={
                GearModifierType.WEAPON_DAMAGE_MIN: 1,
                GearModifierType.WEAPON_DAMAGE_MAX: 2,
            },
            skills=[],
            enchantments=[],
            id=-2,
        )


class DefaultCap(Gear):

    def __init__(self):

        super().__init__(
            name="Cap",
            base=HeadGear_T0(),
            rarity=GearRarity.NORMAL,
            level=1,
            modifiers={
                GearModifierType.ARMOR: 5,
            },
            skills=[],
            enchantments=[],
            id=-3,
        )


class DefaultShirt(Gear):

    def __init__(self):

        super().__init__(
            name="Shirt",
            base=BodyGear_T0(),
            rarity=GearRarity.NORMAL,
            level=1,
            modifiers={
                GearModifierType.ARMOR: 15,
            },
            skills=[],
            enchantments=[],
            id=-4,
        )


class DefaultPants(Gear):

    def __init__(self):

        super().__init__(
            name="Pants",
            base=LegGear_T0(),
            rarity=GearRarity.NORMAL,
            level=1,
            modifiers={
                GearModifierType.ARMOR: 10,
            },
            skills=[],
            enchantments=[],
            id=-5,
        )


class DefaultAccessory(Gear):

    def __init__(self):

        super().__init__(
            name="",
            base=Empty(),
            rarity=GearRarity.NORMAL,
            level=1,
            modifiers={},
            skills=[],
            enchantments=[],
            id=-6,
        )
