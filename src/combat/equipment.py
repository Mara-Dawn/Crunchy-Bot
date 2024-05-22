from combat.gear import DefaultCap, DefaultPants, DefaultShirt, DefaultStick
from combat.gear.gear import Gear
from combat.gear.types import CharacterAttribute, GearModifierType


class CharacterEquipment:

    def __init__(
        self,
        member_id: int,
        weapon: Gear = None,
        head_gear: Gear = None,
        body_gear: Gear = None,
        leg_gear: Gear = None,
        accessory_1: Gear = None,
        accessory_2: Gear = None,
    ):
        self.member_id = member_id
        self.weapon = weapon
        self.head_gear = head_gear
        self.body_gear = body_gear
        self.leg_gear = leg_gear
        self.accessory_1 = accessory_1
        self.accessory_2 = accessory_2
        self.gear: list[Gear] = [
            self.weapon,
            self.head_gear,
            self.body_gear,
            self.leg_gear,
            self.accessory_1,
            self.accessory_2,
        ]

        if self.weapon is None:
            self.weapon = DefaultStick()

        if self.head_gear is None:
            self.head_gear = DefaultCap()

        if self.body_gear is None:
            self.body_gear = DefaultShirt()

        if self.leg_gear is None:
            self.leg_gear = DefaultPants()

        self.attributes: dict[CharacterAttribute, float] = {
            CharacterAttribute.PHYS_DAMAGE_INCREASE: 1,
            CharacterAttribute.MAGIC_DAMAGE_INCREASE: 1,
            CharacterAttribute.HEALING_BONUS: 1,
            CharacterAttribute.CRIT_RATE: 0.1,
            CharacterAttribute.CRIT_DAMAGE: 1.5,
            CharacterAttribute.PHYS_DAMAGE_REDUCTION: 0,
            CharacterAttribute.MAGIC_DAMAGE_REDUCTION: 0,
            CharacterAttribute.MAX_HEALTH: 50,
        }

        self.gear_modifiers: dict[GearModifierType, float] = {}

        for type in GearModifierType:
            self.gear_modifiers[type] = 0

        for item in self.gear:
            if item is None:
                continue
            for modifier_type, modifier in item.modifiers.items():
                self.gear_modifiers[modifier_type] += modifier

        self.attributes[CharacterAttribute.PHYS_DAMAGE_INCREASE] += (
            self.gear_modifiers[GearModifierType.ATTACK] / 100
        )
        self.attributes[CharacterAttribute.MAGIC_DAMAGE_INCREASE] += (
            self.gear_modifiers[GearModifierType.MAGIC] / 100
        )
        self.attributes[CharacterAttribute.CRIT_RATE] += (
            self.gear_modifiers[GearModifierType.CRIT_RATE] / 100
        )
        self.attributes[CharacterAttribute.CRIT_DAMAGE] += (
            self.gear_modifiers[GearModifierType.CRIT_DAMAGE] / 100
        )
        self.attributes[CharacterAttribute.PHYS_DAMAGE_REDUCTION] += (
            self.gear_modifiers[GearModifierType.DEFENSE] / 100
        )
        self.attributes[CharacterAttribute.MAGIC_DAMAGE_REDUCTION] += (
            self.gear_modifiers[GearModifierType.DEFENSE] / 100
        )
        self.attributes[CharacterAttribute.MAX_HEALTH] += self.gear_modifiers[
            GearModifierType.CONSTITUTION
        ]
        self.attributes[CharacterAttribute.HEALING_BONUS] += (
            self.gear_modifiers[GearModifierType.HEALING] / 100
        )
