from datalayer.types import ItemTrigger
from items.item import Item
from items.types import ItemGroup, ItemType, ShopCategory


class SlapBoost(Item):

    def __init__(self, cost: int | None):
        defaultcost = 120

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Massive Bonking Hammer",
            item_type=ItemType.SLAP_BOOST,
            group=ItemGroup.VALUE_MODIFIER,
            shop_category=ShopCategory.SLAP,
            description="For when someone has been extra horny. Powers up your next slap by 5x.",
            emoji="🔨",
            cost=cost,
            value=5,
            view_class=None,
            allow_amount=False,
            base_amount=1,
            max_amount=None,
            trigger=[ItemTrigger.SLAP],
        )
