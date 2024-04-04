from shop.Item import Item
from shop.ItemGroup import ItemGroup
from shop.ItemType import ItemType
from view.ShopCategory import ShopCategory

class Bat(Item):

    def __init__(
        self,
        cost: int|None
    ):
        defaultcost = 1337
        
        if cost is None:
            cost = defaultcost
            
        super().__init__(
            name = 'Baseball Bat',
            type = ItemType.BAT,
            group = ItemGroup.IMMEDIATE_USE,
            shop_category = ShopCategory.INTERACTION,
            description = 'Sneak up on someone and knock them out for 20 minutes, making them unable to use and buy items or gamba their beans.',
            emoji = '💫',
            cost = cost,
            value = 20,
            view_class = 'ShopUserSelectView',
            allow_amount = False,
            base_amount = 1,
            max_amount = None,
            trigger = None
        )