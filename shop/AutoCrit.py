from datalayer.ItemTrigger import ItemTrigger
from shop.Item import Item
from shop.ItemGroup import ItemGroup
from shop.ItemType import ItemType

class AutoCrit(Item):

    def __init__(
        self,
        cost: int|None
    ):
        defaultcost = 100
        
        if cost is None:
            cost = defaultcost
        
        super().__init__(
            name = 'Magic Beans',
            type = ItemType.AUTO_CRIT,
            group = ItemGroup.AUTO_CRIT,
            description = 'Let these rainbow colored little beans guide your next slap, pet or fart to a guaranteed critical hit.',
            emoji = '💥',
            cost = cost,
            value = True,
            view_class = None,
            allow_amount = False,
            base_amount = 1,
            max_amount = None,
            trigger = [ItemTrigger.FART, ItemTrigger.PET, ItemTrigger.SLAP]
        )