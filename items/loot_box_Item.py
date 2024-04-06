from items.item import Item
from items.types import ItemGroup, ItemType, ShopCategory


class LootBoxItem(Item):

    def __init__(self, cost: int | None):
        defaultcost = 150

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Random Treasure Chest",
            item_type=ItemType.LOOTBOX,
            group=ItemGroup.LOOTBOX,
            shop_category=ShopCategory.FUN,
            description="No need to wait for loot box drops, just buy your own!",
            emoji="🧰",
            cost=cost,
            value=None,
            view_class=None,
            allow_amount=False,
            base_amount=1,
            max_amount=None,
            trigger=None,
        )
