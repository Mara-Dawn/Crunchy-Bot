from combat.gear.types import Rarity
from forge.forgable import ForgeInventory, Ingredient
from forge.types import ForgeableType, IngredientFlag, RecipeType
from view.object.types import ObjectType


class ForgeRecipe:

    def __init__(
        self,
        name: str,
        description: str,
        ingredients: tuple[Ingredient, Ingredient, Ingredient],
        result_object_type: ObjectType,
        result_type: ForgeableType,
        recipe_type: RecipeType = None,
        result_rarity: Rarity = None,
        result_level: int = None,
        result_amount: int = 1,
        ingredient_flags: list[IngredientFlag] | None = None,
    ):
        self.name = name
        self.description = description
        self.ingredients = ingredients
        self.result_object_type = result_object_type
        self.result_type = result_type
        self.recipe_type = recipe_type
        self.result_rarity = result_rarity
        self.result_level = result_level
        self.result_amount = result_amount
        self.ingredient_flags = ingredient_flags

    def match(self, inventory: ForgeInventory) -> bool:
        if not inventory.full:
            return False

        if self.ingredient_flags is not None:
            for flag in self.ingredient_flags:
                match flag:
                    case IngredientFlag.SAME_FORGE_TYPE:
                        value = inventory.first.forge_type
                        if not all(
                            ingredient.forge_type == value
                            for ingredient in inventory.items
                        ):
                            return False
                    case IngredientFlag.SAME_OBJECT_TYPE:
                        value = inventory.first.object_type
                        if not all(
                            ingredient.object_type == value
                            for ingredient in inventory.items
                        ):
                            return False
                    case IngredientFlag.SAME_LEVEL:
                        value = inventory.first.level
                        if not all(
                            ingredient.level == value for ingredient in inventory.items
                        ):
                            return False
                    case IngredientFlag.SAME_VALUE:
                        value = inventory.first.value
                        if not all(
                            ingredient.value == value for ingredient in inventory.items
                        ):
                            return False
                    case IngredientFlag.SAME_RARITY:
                        value = inventory.first.rarity
                        if not all(
                            ingredient.rarity == value for ingredient in inventory.items
                        ):
                            return False
                    case IngredientFlag.SAME_SLOT:
                        value = inventory.first.equipment_slot
                        if not all(
                            ingredient.equipment_slot == value
                            for ingredient in inventory.items
                        ):
                            return False

        available = list(self.ingredients)
        for forgeable in inventory.items:
            for ingredient in available:
                if ingredient.match(forgeable):
                    available.remove(ingredient)
                    break
        return len(available) <= 0
