import datetime
from abc import ABC, abstractmethod

from combat.gear.droppable import Droppable
from combat.gear.types import Rarity
from control.combat.combat_gear_manager import CombatGearManager
from control.combat.object_factory import ObjectFactory
from control.controller import Controller
from control.item_manager import ItemManager
from control.logger import BotLogger
from datalayer.database import Database
from events.inventory_event import InventoryEvent
from forge.forgable import ForgeInventory
from forge.recipe import ForgeRecipe
from view.object.types import ObjectType


class RecipeHandler(ABC):

    def __init__(
        self,
        logger: BotLogger,
        database: Database,
        controller: Controller,
    ):
        self.controller = controller
        self.database = database
        self.logger = logger
        self.log_name = "Recipe Handler"
        self.item_manager: ItemManager = controller.get_service(ItemManager)
        self.factory: ObjectFactory = self.controller.get_service(ObjectFactory)
        self.recipes: list[ForgeRecipe] = []

    def _get_min_rarity_and_level(
        self, inventory: ForgeInventory, recipe: ForgeRecipe
    ) -> tuple[Rarity, int]:
        rarity = recipe.result_rarity
        level = recipe.result_level

        if not (rarity is None or level is None):
            return rarity, level

        min_level = None
        min_rarity = None
        for forgeable in inventory.items:
            if level is None and forgeable.level is not None:
                if min_level is None:
                    min_level = forgeable.level
                min_level = min(min_level, forgeable.level)

            if rarity is None and forgeable.rarity is not None:
                if min_rarity is None:
                    min_rarity = forgeable.rarity
                min_rarity_val = CombatGearManager.RARITY_WEIGHTS[min_rarity]
                forgeable_val = CombatGearManager.RARITY_WEIGHTS[forgeable.rarity]
                if min_rarity_val < forgeable_val:
                    min_rarity = forgeable.rarity

        if rarity is None:
            rarity = min_rarity

        if level is None:
            level = min_level

        return rarity, level

    async def consume_inventory(self, inventory: ForgeInventory):
        member = inventory.member
        for forgeable in inventory.items:
            match forgeable.object_type:
                case ObjectType.ITEM:
                    event = InventoryEvent(
                        datetime.datetime.now(),
                        member.guild.id,
                        member.id,
                        forgeable.forge_type,
                        -1,
                    )
                    await self.controller.dispatch_event(event)
                case ObjectType.ENCHANTMENT | ObjectType.GEAR | ObjectType.SKILL:
                    await self.database.delete_gear_by_ids([forgeable.id])
                    self.logger.log(
                        member.guild.id,
                        f"{forgeable.object_type.value} was consumed in the forge by {member.display_name}: lvl.{forgeable.level} {forgeable.rarity.value} {forgeable.name}",
                        cog=self.log_name,
                    )

    def match(self, inventory: ForgeInventory) -> bool:
        return any(recipe.match(inventory) for recipe in self.recipes)

    @abstractmethod
    async def handle(self, inventory: ForgeInventory) -> Droppable | None:
        pass

    def get_recipe(self, inventory: ForgeInventory) -> ForgeRecipe:
        for recipe in self.recipes:
            if recipe.match(inventory):
                return recipe
        return None
