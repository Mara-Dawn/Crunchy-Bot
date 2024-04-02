from shop.Item import Item
from shop.ItemGroup import ItemGroup
from shop.ItemType import ItemType

class Release(Item):

    def __init__(
        self,
        cost: int|None
    ):
        defaultcost = 1000

        if cost is None:
            cost = defaultcost
        
        super().__init__(
            name = 'Get out of Jail Fart',
            type = ItemType.RELEASE,
            group = ItemGroup.IMMEDIATE_USE,
            description = 'Due to dietary advancements your farts can now help a friend out of jail for one time only.',
            emoji = '🔑',
            cost = cost,
            value = None,
            view_class = 'ShopUserSelectView',
            allow_amount = False,
            base_amount = 1,
            max_amount = None,
            trigger = None
        )