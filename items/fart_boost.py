from datalayer.types import ItemTrigger
from items import Item
from items.types import ItemGroup, ItemType, ShopCategory


class FartBoost(Item):

    def __init__(self, cost: int | None):
        defaultcost = 150

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="UK Breakfast Beans",
            item_type=ItemType.FART_BOOST,
            group=ItemGroup.VALUE_MODIFIER,
            shop_category=ShopCategory.FART,
            description="Extremely dangerous, multiplies the power of your next fart by 3.",
            emoji="🤢",
            cost=cost,
            value=3,
            view_class=None,
            allow_amount=False,
            base_amount=1,
            max_amount=None,
            trigger=[ItemTrigger.FART],
        )
