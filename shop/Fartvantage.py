from datalayer.ItemTrigger import ItemTrigger
from shop.Item import Item
from shop.ItemGroup import ItemGroup
from shop.ItemType import ItemType

class Fartvantage(Item):

    def __init__(
        self,
        cost: int|None
    ):
        defaultcost = 69
        
        if cost is None:
            cost = defaultcost
        
        super().__init__(
            name = 'Fast Food Binge',
            type = ItemType.FARTVANTAGE,
            group = ItemGroup.ADVANTAGE,
            description = 'Couldn\'t hold back again, hm? Better go empty your bowels on some poor loser. Rolls your next fart twice and takes the better result.',
            emoji = '🍔',
            cost = cost,
            value = 2,
            view_class = None,
            allow_amount = False,
            base_amount = 1,
            max_amount = None,
            trigger = [ItemTrigger.FART]
        )