from combat.gear.types import Rarity
from forge.forgable import ForgeInventory, Ingredient
from forge.types import ForgeableType, IngredientFlag
from items.types import ItemType
from view.object.types import ObjectType


class ForgeRecipe:

    def __init__(
        self,
        name: str,
        ingredients: tuple[Ingredient, Ingredient, Ingredient],
        result_object_type: ObjectType,
        result_type: ForgeableType,
        result_rarity: Rarity = None,
        result_level: int = None,
        result_amount: int = 1,
        ingredient_flags: list[IngredientFlag] | None = None,
    ):
        self.name = name
        self.ingredients = ingredients
        self.result_object_type = result_object_type
        self.result_type = result_type
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
                        value = self.ingredients[0].forge_type
                        if not all(
                            ingredient.forge_type == value
                            for ingredient in self.ingredients
                        ):
                            return False
                    case IngredientFlag.SAME_OBJECT_TYPE:
                        value = self.ingredients[0].object_type
                        if not all(
                            ingredient.object_type == value
                            for ingredient in self.ingredients
                        ):
                            return False
                    case IngredientFlag.SAME_LEVEL:
                        value = self.ingredients[0].level
                        if not all(
                            ingredient.level == value for ingredient in self.ingredients
                        ):
                            return False
                    case IngredientFlag.SAME_VALUE:
                        value = self.ingredients[0].value
                        if not all(
                            ingredient.value == value for ingredient in self.ingredients
                        ):
                            return False
                    case IngredientFlag.SAME_RARITY:
                        value = self.ingredients[0].rarity
                        if not all(
                            ingredient.rarity == value
                            for ingredient in self.ingredients
                        ):
                            return False

        available = list(self.ingredients)
        for forgeable in inventory.items:
            for ingredient in available:
                if ingredient.match(forgeable):
                    available.remove(ingredient)
                    break
        return len(available) <= 0


class RecipeHandler:

    def __init__(self):
        self.recipes: list[ForgeRecipe] = [
            # Key Upgrades
            ForgeRecipe(
                name="Level 1 Key Upgrade",
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

    def handle(self, inventory: ForgeInventory):
        return any(recipe.match(inventory) for recipe in self.recipes)

    def get_recipe(self, inventory: ForgeInventory) -> ForgeRecipe:
        for recipe in self.recipes:
            if recipe.match(inventory):
                return recipe
        return None
