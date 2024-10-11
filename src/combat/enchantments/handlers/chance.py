from combat.enchantments.enchantment import Enchantment
from combat.enchantments.enchantment_handler import EnchantmentCraftHandler
from combat.enchantments.enchantments import Chance
from combat.gear.gear import Gear
from control.combat.combat_gear_manager import CombatGearManager
from control.controller import Controller


class ChanceHandler(EnchantmentCraftHandler):

    def __init__(self, controller: Controller):
        EnchantmentCraftHandler.__init__(
            self, controller=controller, enchantment=Chance()
        )
        self.gear_manager: CombatGearManager = self.controller.get_service(
            CombatGearManager
        )
        self.database = self.controller.database

    async def handle(self, enchantment: Enchantment, gear: Gear) -> Gear:

        gear.rarity = await self.gear_manager.get_random_rarity(gear.level)

        modifiers = await self.gear_manager.get_random_modifiers(
            gear.base,
            gear.level,
            gear.rarity,
        )
        gear.modifiers = modifiers

        await self.database.delete_user_gear_modifiers(gear.id)
        await self.database.log_user_gear_modifiers(gear.id, gear)
        await self.database.update_gear_rarity(gear.id, gear.rarity)

        new_gear = await self.database.get_gear_by_id(gear.id)

        return new_gear
