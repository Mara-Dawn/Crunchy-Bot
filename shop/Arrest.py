from shop.Item import Item
from shop.ItemGroup import ItemGroup
from shop.ItemType import ItemType

class Arrest(Item):

    def __init__(
        self,
        cost: int|None
    ):
        defaultcost = 1000
        
        if cost is None:
            cost = defaultcost
            
        super().__init__(
            name = 'Citizens Arrest',
            type = ItemType.ARREST,
            group = ItemGroup.IMMEDIATE_USE,
            description = 'Take the law into your own hands and arrest a user of choice for 30 minutes.',
            emoji = '🚨',
            cost = cost,
            value = None,
            view_class = 'ShopUserSelectView',
            allow_amount = False,
            base_amount = 1,
            max_amount = None,
            trigger = None
        )