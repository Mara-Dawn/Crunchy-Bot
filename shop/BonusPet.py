from datalayer.ItemTrigger import ItemTrigger
from shop.Item import Item
from shop.ItemGroup import ItemGroup
from shop.ItemType import ItemType
from view.ShopCategory import ShopCategory

class BonusPet(Item):

    def __init__(
        self,
        cost: int|None
    ):
        defaultcost = 35
        
        if cost is None:
            cost = defaultcost
            
        super().__init__(
            name = 'Bonus Pet',
            type = ItemType.BONUS_PET,
            group = ItemGroup.BONUS_ATTEMPT,
            shop_category = ShopCategory.PET,
            description = 'Allows you to continue giving pets to a jailed person after using your guaranteed one.',
            emoji = '🥰',
            cost = cost,
            value = True,
            view_class = None,
            allow_amount = False,
            base_amount = 1,
            max_amount = None,
            trigger = [ItemTrigger.PET]
        )
            