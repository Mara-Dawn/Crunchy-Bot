from combat.gear.bases import BodyGear_T0, HeadGear_T0, LegGear_T0, Stick_T0, Wand_T0
from combat.gear.gear import Gear
from combat.gear.types import GearModifierType, GearRarity

# Starting Gear


class DefaultStick(Gear):

    def __init__(self):

        super().__init__(
            name="",
            base=Stick_T0(),
            rarity=GearRarity.NORMAL,
            level=1,
            modifiers={
                GearModifierType.WEAPON_DAMAGE_MIN: 1,
                GearModifierType.WEAPON_DAMAGE_MAX: 2,
            },
            skills=[],
            enchantments=[],
        )


class DefaultWand(Gear):

    def __init__(self):

        super().__init__(
            name="",
            base=Wand_T0(),
            rarity=GearRarity.NORMAL,
            level=1,
            modifiers={
                GearModifierType.WEAPON_DAMAGE_MIN: 1,
                GearModifierType.WEAPON_DAMAGE_MAX: 2,
            },
            skills=[],
            enchantments=[],
        )


class DefaultCap(Gear):

    def __init__(self):

        super().__init__(
            name="",
            base=HeadGear_T0(),
            rarity=GearRarity.NORMAL,
            level=1,
            modifiers={
                GearModifierType.ARMOR: 5,
            },
            skills=[],
            enchantments=[],
        )


class DefaultShirt(Gear):

    def __init__(self):

        super().__init__(
            name="",
            base=BodyGear_T0(),
            rarity=GearRarity.NORMAL,
            level=1,
            modifiers={
                GearModifierType.ARMOR: 15,
            },
            skills=[],
            enchantments=[],
        )


class DefaultPants(Gear):

    def __init__(self):

        super().__init__(
            name="",
            base=LegGear_T0(),
            rarity=GearRarity.NORMAL,
            level=1,
            modifiers={
                GearModifierType.ARMOR: 10,
            },
            skills=[],
            enchantments=[],
        )
