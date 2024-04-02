from datalayer.ItemTrigger import ItemTrigger
from shop.Item import Item
from shop.ItemGroup import ItemGroup
from shop.ItemType import ItemType

class FartStabilizer(Item):

    def __init__(
        self,
        cost: int|None
    ):
        defaultcost = 45
        
        if cost is None:
            cost = defaultcost
        
        super().__init__(
            name = 'Ass ACOG',
            type = ItemType.FART_STABILIZER,
            group = ItemGroup.STABILIZER,
            description = 'Stabilizes your aim and increases your rectal precision. Your next fart cannot roll below 0.',
            emoji = '🔭',
            cost = cost,
            value = 10,
            view_class = None,
            allow_amount = False,
            base_amount = 1,
            max_amount = None,
            trigger = [ItemTrigger.FART]
        )