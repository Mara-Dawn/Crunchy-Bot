from forge.forgable import Forgeable


class ForgeRecipe:

    def __init__(
        self,
        name: str,
        ingredients: tuple[Forgeable, Forgeable, Forgeable],
        result: Forgeable,
        result_amount: int = 1,
    ):
        self.name = name
        self.ingredients = ingredients
        self.result = result
        self.result_amount = result_amount
