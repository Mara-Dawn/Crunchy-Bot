from datalayer.ItemTrigger import ItemTrigger
from shop.Item import Item
from shop.ItemGroup import ItemGroup
from shop.ItemType import ItemType

class ExplosiveFart(Item):

    def __init__(
        self,
        cost: int|None
    ):
        defaultcost = 10000
        
        if cost is None:
            cost = defaultcost
            
        description =  'You strayed too far from Gods guiding light and tasted the forbidden fruit you found behind grandmas fridge. '
        description += 'Once released, the storm brewing inside you carries up to 5 random people directly to the shadow realm for 5-10 hours.\n'
        description += '(only affects people with more than 500 beans)'
        
        super().__init__(
            name = 'Explosive Diarrhea',
            type = ItemType.EXPLOSIVE_FART,
            group = ItemGroup.IMMEDIATE_USE,
            description = description,
            emoji = '😨',
            cost = cost,
            value = 1,
            view_class = 'ShopConfirmView',
            allow_amount = False,
            base_amount = 1,
            max_amount = None,
            trigger = None
        )