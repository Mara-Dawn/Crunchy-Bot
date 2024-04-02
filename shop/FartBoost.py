from datalayer.ItemTrigger import ItemTrigger
from shop.Item import Item
from shop.ItemGroup import ItemGroup
from shop.ItemType import ItemType

class FartBoost(Item):

    def __init__(
        self,
        cost: int|None
    ):
        defaultcost = 150
        
        if cost is None:
            cost = defaultcost
            
        super().__init__(
            name = 'UK Breakfast Beans',
            type = ItemType.FART_BOOST,
            group = ItemGroup.VALUE_MODIFIER,
            description = 'Extremely dangerous, multiplies the power of your next fart by 3.',
            emoji = '🤢',
            cost = cost,
            value = 3,
            view_class = None,
            allow_amount = False,
            base_amount = 1,
            max_amount = None,
            trigger = [ItemTrigger.FART]
        )