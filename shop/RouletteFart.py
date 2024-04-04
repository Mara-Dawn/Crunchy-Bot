from shop.Item import Item
from shop.ItemGroup import ItemGroup
from shop.ItemType import ItemType

class RouletteFart(Item):

    def __init__(
        self,
        cost: int|None
    ):
        defaultcost = 500
        
        if cost is None:
            cost = defaultcost
            
        super().__init__(
            name = 'Russian Roulette',
            type = ItemType.ROULETTE_FART,
            group = ItemGroup.IMMEDIATE_USE,
            description = 'After a night of heavy drinking you decide to gamble on a fart to prank your friend. 50% chance to jail the target, 50% chance to shit yourself and go to jail instead. (30 minutes)',
            emoji = '🔫',
            cost = cost,
            value = None,
            view_class = 'ShopUserSelectView',
            allow_amount = False,
            base_amount = 1,
            max_amount = None,
            trigger = None
        )