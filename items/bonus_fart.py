from datalayer.types import ItemTrigger
from items.item import Item
from items.types import ItemGroup, ItemType, ShopCategory


class BonusFart(Item):

    def __init__(self, cost: int | None):
        defaultcost = 100

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Bonus Fart",
            item_type=ItemType.BONUS_FART,
            group=ItemGroup.BONUS_ATTEMPT,
            shop_category=ShopCategory.FART,
            description="Allows you to continue farting on a jailed person after using your guaranteed one.",
            emoji="😂",
            cost=cost,
            value=True,
            view_class=None,
            allow_amount=False,
            base_amount=1,
            max_amount=None,
            trigger=[ItemTrigger.FART],
        )
