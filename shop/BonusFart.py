from datalayer.ItemTrigger import ItemTrigger
from shop.Item import Item
from shop.ItemGroup import ItemGroup
from shop.ItemType import ItemType

class BonusFart(Item):

    def __init__(
        self,
        cost: int|None
    ):
        defaultcost = 100
        
        if cost is None:
            cost = defaultcost
            
        super().__init__(
            name = 'Bonus Fart',
            type = ItemType.BONUS_FART,
            group = ItemGroup.BONUS_ATTEMPT,
            description = 'Allows you to continue farting on a jailed person after using your guaranteed one.',
            emoji = '😂',
            cost = cost,
            value = True,
            view_class = None,
            allow_amount = False,
            base_amount = 1,
            max_amount = None,
            trigger = [ItemTrigger.FART]
        )