from combat.gear.bases import (
    DefaultBody,
    DefaultHead,
    DefaultLegs,
    DefaultMagical,
    DefaultPhys,
    Empty,
)
from combat.gear.gear import Gear
from combat.gear.types import GearModifierType, Rarity

# Starting Gear


class DefaultStick(Gear):

    def __init__(self):

        super().__init__(
            name=None,
            base=DefaultPhys(),
            rarity=Rarity.DEFAULT,
            level=1,
            modifiers={
                GearModifierType.WEAPON_DAMAGE_MIN: 7,
                GearModifierType.WEAPON_DAMAGE_MAX: 9,
            },
            skills=[],
            enchantments=[],
            id=-1,
        )


class DefaultWand(Gear):

    def __init__(self):

        super().__init__(
            name=None,
            base=DefaultMagical(),
            rarity=Rarity.DEFAULT,
            level=1,
            modifiers={
                GearModifierType.WEAPON_DAMAGE_MIN: 7,
                GearModifierType.WEAPON_DAMAGE_MAX: 9,
            },
            skills=[],
            enchantments=[],
            id=-2,
        )


class DefaultCap(Gear):

    def __init__(self):

        super().__init__(
            name=None,
            base=DefaultHead(),
            rarity=Rarity.DEFAULT,
            level=1,
            modifiers={
                GearModifierType.ARMOR: 4,
            },
            skills=[],
            enchantments=[],
            id=-3,
        )


class DefaultShirt(Gear):

    def __init__(self):

        super().__init__(
            name=None,
            base=DefaultBody(),
            rarity=Rarity.DEFAULT,
            level=1,
            modifiers={
                GearModifierType.ARMOR: 12,
            },
            skills=[],
            enchantments=[],
            id=-4,
        )


class DefaultPants(Gear):

    def __init__(self):

        super().__init__(
            name=None,
            base=DefaultLegs(),
            rarity=Rarity.DEFAULT,
            level=1,
            modifiers={
                GearModifierType.ARMOR: 8,
            },
            skills=[],
            enchantments=[],
            id=-5,
        )


class DefaultAccessory1(Gear):

    def __init__(self):

        super().__init__(
            name="",
            base=Empty(),
            rarity=Rarity.DEFAULT,
            level=1,
            modifiers={},
            skills=[],
            enchantments=[],
            id=-6,
        )


class DefaultAccessory2(Gear):

    def __init__(self):

        super().__init__(
            name="",
            base=Empty(),
            rarity=Rarity.DEFAULT,
            level=1,
            modifiers={},
            skills=[],
            enchantments=[],
            id=-7,
        )
