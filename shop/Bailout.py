from shop.Item import Item
from shop.ItemGroup import ItemGroup
from shop.ItemType import ItemType
from view.ShopCategory import ShopCategory
class Bailout(Item):

    def __init__(
        self,
        cost: int|None
    ):
        defaultcost = 2500
        
        if cost is None:
            cost = defaultcost

        super().__init__(
            name = 'Bribe the Mods',
            type = ItemType.BAILOUT,
            group = ItemGroup.IMMEDIATE_USE,
            shop_category = ShopCategory.JAIL,
            description = 'Pay off the mods to let you out of jail early.',
            emoji = '🗿',
            cost = cost,
            value = None,
            view_class = 'ShopConfirmView',
            allow_amount = False,
            base_amount = 1,
            max_amount = None,
            trigger = None
        )