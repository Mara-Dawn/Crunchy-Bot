from items import Item
from items.types import ItemGroup, ItemType, ShopCategory


class LotteryTicket(Item):

    def __init__(self, cost: int | None):
        defaultcost = 100

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Lottery Ticket",
            item_type=ItemType.LOTTERY_TICKET,
            group=ItemGroup.LOTTERY,
            shop_category=ShopCategory.FUN,
            description="Enter the Weekly Crunchy Bean Lottery© and win big! Max 3 tickets per person.",
            emoji="🎫",
            cost=cost,
            value=1,
            view_class=None,
            allow_amount=False,
            base_amount=1,
            max_amount=3,
            trigger=None,
        )
