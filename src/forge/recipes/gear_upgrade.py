from combat.gear.droppable import Droppable
from combat.gear.types import Rarity
from control.combat.combat_gear_manager import CombatGearManager
from control.controller import Controller
from control.logger import BotLogger
from datalayer.database import Database
from forge.forgable import ForgeInventory, Ingredient
from forge.recipe import ForgeRecipe
from forge.recipe_handler import RecipeHandler
from forge.types import IngredientFlag, RecipeType
from view.object.types import ObjectType


class GearRecipeHandler(RecipeHandler):

    UPGRADE_MAP = {
        Rarity.COMMON: Rarity.UNCOMMON,
        Rarity.UNCOMMON: Rarity.RARE,
        Rarity.RARE: Rarity.LEGENDARY,
    }

    def __init__(
        self,
        logger: BotLogger,
        database: Database,
        controller: Controller,
    ):
        super().__init__(logger, database, controller)
        self.recipes: list[ForgeRecipe] = [
            ForgeRecipe(
                name="Upgrade Base Rarity",
                description=(
                    "Uses three gear pieces of the same base, rarity and gear slot and "
                    "returns a gear piece of the same base type and slot of the next higher rarity.\n"
                    "Item level will be equal to the lowest level ingredient."
                ),
                recipe_type=RecipeType.GEAR_BASE_RARITY_UPGRADE,
                ingredients=(
                    Ingredient(
                        object_type=ObjectType.GEAR,
                    ),
                    Ingredient(
                        object_type=ObjectType.GEAR,
                    ),
                    Ingredient(
                        object_type=ObjectType.GEAR,
                    ),
                ),
                ingredient_flags=[
                    IngredientFlag.SAME_OBJECT_TYPE,
                    IngredientFlag.SAME_SLOT,
                    IngredientFlag.SAME_RARITY,
                    IngredientFlag.SAME_FORGE_TYPE,
                ],
                result_object_type=ObjectType.GEAR,
                result_type=None,
            ),
            ForgeRecipe(
                name="Upgrade Rarity",
                description=(
                    "Uses three gear pieces of the same rarity and gear slot and "
                    "returns a random gear piece of the same slot of the next higher rarity.\n"
                    "Item level will be equal to the lowest level ingredient."
                ),
                recipe_type=RecipeType.GEAR_RARITY_UPGRADE,
                ingredients=(
                    Ingredient(
                        object_type=ObjectType.GEAR,
                    ),
                    Ingredient(
                        object_type=ObjectType.GEAR,
                    ),
                    Ingredient(
                        object_type=ObjectType.GEAR,
                    ),
                ),
                ingredient_flags=[
                    IngredientFlag.SAME_OBJECT_TYPE,
                    IngredientFlag.SAME_SLOT,
                    IngredientFlag.SAME_RARITY,
                ],
                result_object_type=ObjectType.GEAR,
                result_type=None,
            ),
            ForgeRecipe(
                name="Reroll with same Base",
                description=(
                    "Uses three gear pieces with the same base and "
                    "returns a random gear piece of the same base.\n"
                    "Item level will be equal to the lowest level ingredient.\n"
                    "Item rarity will be equal or greater than the lowest rarity ingredient."
                ),
                recipe_type=RecipeType.GEAR_BASE_REROLL,
                ingredients=(
                    Ingredient(
                        object_type=ObjectType.GEAR,
                    ),
                    Ingredient(
                        object_type=ObjectType.GEAR,
                    ),
                    Ingredient(
                        object_type=ObjectType.GEAR,
                    ),
                ),
                ingredient_flags=[
                    IngredientFlag.SAME_OBJECT_TYPE,
                    IngredientFlag.SAME_FORGE_TYPE,
                ],
                result_object_type=ObjectType.GEAR,
                result_type=None,
            ),
            ForgeRecipe(
                name="Reroll Gear with same Slot",
                description=(
                    "Uses three gear pieces of the same gear slot and "
                    "returns a random gear piece of the same slot.\n"
                    "Item level will be equal to the lowest level ingredient.\n"
                    "Item rarity will be equal or greater than the lowest rarity ingredient."
                ),
                recipe_type=RecipeType.GEAR_SLOT_REROLL,
                ingredients=(
                    Ingredient(
                        object_type=ObjectType.GEAR,
                    ),
                    Ingredient(
                        object_type=ObjectType.GEAR,
                    ),
                    Ingredient(
                        object_type=ObjectType.GEAR,
                    ),
                ),
                ingredient_flags=[
                    IngredientFlag.SAME_OBJECT_TYPE,
                    IngredientFlag.SAME_SLOT,
                ],
                result_object_type=ObjectType.GEAR,
                result_type=None,
            ),
            ForgeRecipe(
                name="Reroll Gear",
                description=(
                    "Uses three unrelated gear pieces and "
                    "returns a random gear piece. "
                    "Item level will be equal to the lowest level ingredient. "
                    "Item rarity will be equal or greater than the lowest rarity ingredient."
                ),
                recipe_type=RecipeType.GEAR_FULL_REROLL,
                ingredients=(
                    Ingredient(
                        object_type=ObjectType.GEAR,
                    ),
                    Ingredient(
                        object_type=ObjectType.GEAR,
                    ),
                    Ingredient(
                        object_type=ObjectType.GEAR,
                    ),
                ),
                ingredient_flags=[
                    IngredientFlag.SAME_OBJECT_TYPE,
                ],
                result_object_type=ObjectType.GEAR,
                result_type=None,
            ),
        ]

        self.gear_manager: CombatGearManager = self.controller.get_service(
            CombatGearManager
        )

    async def handle(self, inventory: ForgeInventory) -> Droppable | None:
        recipe = self.get_recipe(inventory)
        if recipe is None:
            return None

        result = None

        rarity, level = self._get_min_rarity_and_level(inventory, recipe)

        member = inventory.member

        match recipe.recipe_type:
            case RecipeType.GEAR_RARITY_UPGRADE:
                if rarity in self.UPGRADE_MAP:
                    rarity = self.UPGRADE_MAP[rarity]
                droppable_base = await self.gear_manager.get_random_base(
                    guild_id=member.guild.id,
                    item_level=level,
                    exclude_enchantments=True,
                    gear_slot=inventory.first.equipment_slot,
                )
            case RecipeType.GEAR_BASE_RARITY_UPGRADE:
                if rarity in self.UPGRADE_MAP:
                    rarity = self.UPGRADE_MAP[rarity]
                droppable_base = await self.factory.get_base(inventory.first.forge_type)
            case RecipeType.GEAR_BASE_REROLL:
                rarity = await self.gear_manager.get_random_rarity(
                    level, min_rarity=rarity
                )
                droppable_base = await self.factory.get_base(inventory.first.forge_type)
            case RecipeType.GEAR_SLOT_REROLL:
                rarity = await self.gear_manager.get_random_rarity(
                    level, min_rarity=rarity
                )
                droppable_base = await self.gear_manager.get_random_base(
                    guild_id=member.guild.id,
                    item_level=level,
                    exclude_enchantments=True,
                    exclude_skills=True,
                    gear_slot=inventory.first.equipment_slot,
                )
            case RecipeType.GEAR_FULL_REROLL:
                rarity = await self.gear_manager.get_random_rarity(
                    level, min_rarity=rarity
                )
                droppable_base = await self.gear_manager.get_random_base(
                    guild_id=member.guild.id,
                    item_level=level,
                    exclude_enchantments=True,
                    exclude_skills=True,
                )
            case _:
                droppable_base = await self.factory.get_base(recipe.result_type)

        result = await self.gear_manager.generate_specific_drop(
            member_id=member.id,
            guild_id=member.guild.id,
            item_level=level,
            base=droppable_base,
            rarity=rarity,
        )

        return result
