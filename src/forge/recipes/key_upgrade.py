from combat.gear.droppable import Droppable
from control.controller import Controller
from control.logger import BotLogger
from datalayer.database import Database
from forge.forgable import ForgeInventory, Ingredient
from forge.recipe import ForgeRecipe
from forge.recipe_handler import RecipeHandler
from items.types import ItemType
from view.object.types import ObjectType


class KeyRecipeHandler(RecipeHandler):

    def __init__(
        self,
        logger: BotLogger,
        database: Database,
        controller: Controller,
    ):
        super().__init__(logger, database, controller)
        self.recipes: list[ForgeRecipe] = [
            ForgeRecipe(
                name="Level 1 Key Upgrade",
                description=(
                    "Combines three keys of the same level into one of the next higher level."
                ),
                ingredients=(
                    Ingredient(
                        forge_type=ItemType.ENCOUNTER_KEY_1,
                    ),
                    Ingredient(
                        forge_type=ItemType.ENCOUNTER_KEY_1,
                    ),
                    Ingredient(
                        forge_type=ItemType.ENCOUNTER_KEY_1,
                    ),
                ),
                result_object_type=ObjectType.ITEM,
                result_type=ItemType.ENCOUNTER_KEY_2,
            ),
            ForgeRecipe(
                name="Level 2 Key Upgrade",
                description=(
                    "Combines three keys of the same level into one of the next higher level."
                ),
                ingredients=(
                    Ingredient(
                        forge_type=ItemType.ENCOUNTER_KEY_2,
                    ),
                    Ingredient(
                        forge_type=ItemType.ENCOUNTER_KEY_2,
                    ),
                    Ingredient(
                        forge_type=ItemType.ENCOUNTER_KEY_2,
                    ),
                ),
                result_object_type=ObjectType.ITEM,
                result_type=ItemType.ENCOUNTER_KEY_3,
            ),
            ForgeRecipe(
                name="Level 3 Key Upgrade",
                description=(
                    "Combines three keys of the same level into one of the next higher level."
                ),
                ingredients=(
                    Ingredient(
                        forge_type=ItemType.ENCOUNTER_KEY_3,
                    ),
                    Ingredient(
                        forge_type=ItemType.ENCOUNTER_KEY_3,
                    ),
                    Ingredient(
                        forge_type=ItemType.ENCOUNTER_KEY_3,
                    ),
                ),
                result_object_type=ObjectType.ITEM,
                result_type=ItemType.ENCOUNTER_KEY_4,
            ),
            ForgeRecipe(
                name="Level 4 Key Upgrade",
                description=(
                    "Combines three keys of the same level into one of the next higher level."
                ),
                ingredients=(
                    Ingredient(
                        forge_type=ItemType.ENCOUNTER_KEY_4,
                    ),
                    Ingredient(
                        forge_type=ItemType.ENCOUNTER_KEY_4,
                    ),
                    Ingredient(
                        forge_type=ItemType.ENCOUNTER_KEY_4,
                    ),
                ),
                result_object_type=ObjectType.ITEM,
                result_type=ItemType.ENCOUNTER_KEY_5,
            ),
            ForgeRecipe(
                name="Level 5 Key Upgrade",
                description=(
                    "Combines three keys of the same level into one of the next higher level."
                ),
                ingredients=(
                    Ingredient(
                        forge_type=ItemType.ENCOUNTER_KEY_5,
                    ),
                    Ingredient(
                        forge_type=ItemType.ENCOUNTER_KEY_5,
                    ),
                    Ingredient(
                        forge_type=ItemType.ENCOUNTER_KEY_5,
                    ),
                ),
                result_object_type=ObjectType.ITEM,
                result_type=ItemType.ENCOUNTER_KEY_6,
            ),
            ForgeRecipe(
                name="Level 6 Key Upgrade",
                description=(
                    "Combines three keys of the same level into one of the next higher level."
                ),
                ingredients=(
                    Ingredient(
                        forge_type=ItemType.ENCOUNTER_KEY_6,
                    ),
                    Ingredient(
                        forge_type=ItemType.ENCOUNTER_KEY_6,
                    ),
                    Ingredient(
                        forge_type=ItemType.ENCOUNTER_KEY_6,
                    ),
                ),
                result_object_type=ObjectType.ITEM,
                result_type=ItemType.ENCOUNTER_KEY_7,
            ),
            ForgeRecipe(
                name="Level 6 Key Upgrade",
                description=(
                    "Combines three keys of the same level into one of the next higher level."
                ),
                ingredients=(
                    Ingredient(
                        forge_type=ItemType.ENCOUNTER_KEY_6,
                    ),
                    Ingredient(
                        forge_type=ItemType.ENCOUNTER_KEY_6,
                    ),
                    Ingredient(
                        forge_type=ItemType.ENCOUNTER_KEY_6,
                    ),
                ),
                result_object_type=ObjectType.ITEM,
                result_type=ItemType.ENCOUNTER_KEY_7,
            ),
        ]

    async def handle(self, inventory: ForgeInventory) -> Droppable | None:
        recipe = self.get_recipe(inventory)
        if recipe is None:
            return None

        result = None

        member = inventory.member

        item = await self.item_manager.get_item(member.guild.id, recipe.result_type)
        result = await self.item_manager.give_item(
            member.guild.id, member.id, item, recipe.result_amount
        )
        return result
