from datalayer.ItemTrigger import ItemTrigger
from shop.Item import Item
from shop.ItemGroup import ItemGroup
from shop.ItemType import ItemType
from view.ShopCategory import ShopCategory

class PetBoost(Item):

    def __init__(
        self,
        cost: int|None
    ):
        defaultcost = 120
        
        if cost is None:
            cost = defaultcost
            
        super().__init__(
            name = 'Big Mama Bear Hug',
            type = ItemType.PET_BOOST,
            group = ItemGroup.VALUE_MODIFIER,
            shop_category = ShopCategory.PET,
            description = 'When a normal pet just isnt enough. Powers up your next pet by 5x.',
            emoji = '🧸',
            cost = cost,
            value = 5,
            view_class = None,
            allow_amount = False,
            base_amount = 1,
            max_amount = None,
            trigger = [ItemTrigger.PET]
        )

            