from datalayer.ItemTrigger import ItemTrigger
from shop.Item import Item
from shop.ItemGroup import ItemGroup
from shop.ItemType import ItemType
from view.ShopCategory import ShopCategory

class GigaFart(Item):

    def __init__(
        self,
        cost: int|None
    ):
        defaultcost = 500
        
        if cost is None:
            cost = defaultcost
            
        super().__init__(
            name = 'Shady 4am Chinese Takeout',
            type = ItemType.GIGA_FART,
            group = ItemGroup.VALUE_MODIFIER,
            shop_category = ShopCategory.FART,
            description = 'Works better than any laxative and boosts the pressure of your next fart by x10. Try not to hurt yourself.',
            emoji = '💀',
            cost = cost,
            value = 10,
            view_class = None,
            allow_amount = False,
            base_amount = 1,
            max_amount = None,
            trigger = [ItemTrigger.FART]
        )