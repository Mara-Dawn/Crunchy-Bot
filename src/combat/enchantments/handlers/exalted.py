import random

from combat.enchantments.enchantment import Enchantment
from combat.enchantments.enchantment_handler import EnchantmentCraftHandler
from combat.enchantments.enchantments import Exalted
from combat.gear.gear import Gear
from combat.gear.types import GearModifierType, Rarity
from control.combat.combat_gear_manager import CombatGearManager
from control.controller import Controller


class ExaltedHandler(EnchantmentCraftHandler):

    UPGRADE_MAP = {
        Rarity.COMMON: Rarity.UNCOMMON,
        Rarity.UNCOMMON: Rarity.RARE,
        Rarity.RARE: Rarity.LEGENDARY,
    }

    def __init__(self, controller: Controller):
        EnchantmentCraftHandler.__init__(
            self, controller=controller, enchantment=Exalted()
        )
        self.gear_manager: CombatGearManager = self.controller.get_service(
            CombatGearManager
        )
        self.database = self.controller.database

    async def handle(self, enchantment: Enchantment, gear: Gear) -> Gear:
        if enchantment.rarity != gear.rarity:
            return gear

        existing_modifiers: dict[GearModifierType, float] = gear.modifiers

        allowed_modifiers = gear.base.get_allowed_modifiers()
        possible_modifiers = [
            mod for mod in allowed_modifiers if mod not in existing_modifiers
        ]

        new_modifier_type = random.choice(possible_modifiers)

        new_modifier_value = await self.gear_manager.roll_modifier_value(
            gear.base, gear.level, new_modifier_type
        )

        gear.modifiers[new_modifier_type] = new_modifier_value

        new_rarity = self.UPGRADE_MAP[enchantment.rarity]

        await self.database.delete_user_gear_modifiers(gear.id)
        await self.database.log_user_gear_modifiers(gear.id, gear)
        await self.database.update_gear_rarity(gear.id, new_rarity)

        new_gear = await self.database.get_gear_by_id(gear.id)

        return new_gear
