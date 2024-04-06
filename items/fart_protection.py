from datalayer.types import ItemTrigger
from items import Item
from items.types import ItemGroup, ItemType, ShopCategory


class FartProtection(Item):

    def __init__(self, cost: int | None):
        defaultcost = 175

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Your Uncle's old Hazmat Suit",
            item_type=ItemType.FART_PROTECTION,
            group=ItemGroup.PROTECTION,
            shop_category=ShopCategory.INTERACTION,
            description="According to him his grandpa took it from a dead guy in ww2. The next 5 interactions negatively affecting your jailtime will be reduced by 50%",
            emoji="☣",
            cost=cost,
            value=0.5,
            view_class=None,
            allow_amount=False,
            base_amount=5,
            max_amount=5,
            trigger=[ItemTrigger.FART, ItemTrigger.SLAP],
        )
