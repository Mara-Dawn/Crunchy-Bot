from control.controller import Controller
from control.logger import BotLogger
from datalayer.database import Database
from forge.forgable import ForgeInventory
from forge.recipe import ForgeRecipe
from forge.recipe_handler import RecipeHandler
from forge.recipes.gear_upgrade import GearRecipeHandler
from forge.recipes.key_upgrade import KeyRecipeHandler


class RecipeHandlerCollection:

    def __init__(
        self,
        logger: BotLogger,
        database: Database,
        controller: Controller,
    ):
        self.handlers: list[RecipeHandler] = [
            KeyRecipeHandler(logger, database, controller),
            GearRecipeHandler(logger, database, controller),
        ]

    def match(self, inventory: ForgeInventory) -> bool:
        return any(handler.match(inventory) for handler in self.handlers)

    def get_handler(self, inventory: ForgeInventory) -> RecipeHandler | None:
        for handler in self.handlers:
            if handler.match(inventory):
                return handler
        return None

    def get_recipe(self, inventory: ForgeInventory) -> ForgeRecipe:
        for handler in self.handlers:
            recipe = handler.get_recipe(inventory)
            if recipe is not None:
                return recipe
        return None
