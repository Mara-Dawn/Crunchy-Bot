from items import Item
from items.types import ItemGroup, ItemType, ShopCategory


class Bailout(Item):

    def __init__(self, cost: int | None):
        defaultcost = 2500

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Bribe the Mods",
            item_type=ItemType.BAILOUT,
            group=ItemGroup.IMMEDIATE_USE,
            shop_category=ShopCategory.JAIL,
            description="Pay off the mods to let you out of jail early.",
            emoji="🗿",
            cost=cost,
            value=None,
            view_class="ShopConfirmView",
            allow_amount=False,
            base_amount=1,
            max_amount=None,
            trigger=None,
        )
