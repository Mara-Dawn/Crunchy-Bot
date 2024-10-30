import random

from combat.enchantments.enchantment import Enchantment
from combat.enchantments.enchantment_handler import EnchantmentCraftHandler
from combat.enchantments.enchantments import Exalted
from combat.gear.gear import Gear
from combat.gear.types import Rarity
from control.combat.combat_gear_manager import CombatGearManager
from control.controller import Controller


class NullHandler(EnchantmentCraftHandler):

    DOWNGRADE_MAP = {
        Rarity.UNCOMMON: Rarity.COMMON,
        Rarity.RARE: Rarity.UNCOMMON,
        Rarity.LEGENDARY: Rarity.RARE,
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
        if gear.rarity not in self.DOWNGRADE_MAP:
            return gear

        allowed_modifiers = gear.base.get_allowed_modifiers()
        possible_modifiers = [mod for mod in gear.modifiers if mod in allowed_modifiers]

        removed = random.choice(possible_modifiers)

        del gear.modifiers[removed]

        new_rarity = self.DOWNGRADE_MAP[gear.rarity]

        await self.database.delete_user_gear_modifiers(gear.id)
        await self.database.log_user_gear_modifiers(gear.id, gear)
        await self.database.update_gear_rarity(gear.id, new_rarity)

        new_gear = await self.database.get_gear_by_id(gear.id)

        return new_gear
