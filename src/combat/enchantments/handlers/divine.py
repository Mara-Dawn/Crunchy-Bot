from combat.enchantments.enchantment import Enchantment
from combat.enchantments.enchantment_handler import EnchantmentCraftHandler
from combat.enchantments.enchantments import Divine
from combat.gear.gear import Gear
from combat.gear.types import GearModifierType
from control.combat.combat_gear_manager import CombatGearManager
from control.controller import Controller


class DivineHandler(EnchantmentCraftHandler):

    def __init__(self, controller: Controller):
        EnchantmentCraftHandler.__init__(
            self, controller=controller, enchantment=Divine()
        )
        self.gear_manager: CombatGearManager = self.controller.get_service(
            CombatGearManager
        )
        self.database = self.controller.database

    async def handle(self, enchantment: Enchantment, gear: Gear) -> Gear:
        modifiers: dict[GearModifierType, float] = {}
        for modifier_type, _ in gear.modifiers.items():
            modifiers[modifier_type] = await self.gear_manager.roll_modifier_value(
                gear.base, gear.level, modifier_type
            )

        gear.modifiers = modifiers

        await self.database.delete_user_gear_modifiers(gear.id)
        await self.database.log_user_gear_modifiers(gear.id, gear)

        new_gear = await self.database.get_gear_by_id(gear.id)

        return new_gear
