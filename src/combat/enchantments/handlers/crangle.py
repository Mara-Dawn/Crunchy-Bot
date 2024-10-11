import random

from combat.enchantments.enchantment import Enchantment
from combat.enchantments.enchantment_handler import EnchantmentCraftHandler
from combat.enchantments.enchantments import Crangle
from combat.gear.gear import Gear
from combat.gear.types import GearModifierType
from control.combat.combat_gear_manager import CombatGearManager
from control.controller import Controller


class CrangleHandler(EnchantmentCraftHandler):

    MODIFIERS = [
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
    ]

    NEGATIVE_CHANCE = 0.15
    CRANGLE_SCALING = 1.3

    def __init__(self, controller: Controller):
        EnchantmentCraftHandler.__init__(
            self, controller=controller, enchantment=Crangle()
        )
        self.gear_manager: CombatGearManager = self.controller.get_service(
            CombatGearManager
        )
        self.database = self.controller.database

    async def handle(self, enchantment: Enchantment, gear: Gear) -> Gear:

        modifiers = {}

        modifier_count = CombatGearManager.MODIFIER_COUNT[gear.rarity]

        modifier_types = random.sample(self.MODIFIERS, k=modifier_count)
        modifier_types.extend(gear.base.modifiers)

        for modifier_type in modifier_types:
            value = await self.gear_manager.roll_modifier_value(
                gear.base,
                gear.level,
                modifier_type,
            )
            if modifier_type not in [
                GearModifierType.WEAPON_DAMAGE_MAX,
                GearModifierType.WEAPON_DAMAGE_MIN,
            ]:
                value *= self.CRANGLE_SCALING
            if random.random() < self.NEGATIVE_CHANCE:
                value *= -1

            modifiers[modifier_type] = value

        modifiers[GearModifierType.CRANGLED] = 1

        gear.modifiers = modifiers

        await self.database.delete_user_gear_modifiers(gear.id)
        await self.database.log_user_gear_modifiers(gear.id, gear)

        new_gear = await self.database.get_gear_by_id(gear.id)

        return new_gear
