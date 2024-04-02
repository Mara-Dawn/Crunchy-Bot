from datalayer.ItemTrigger import ItemTrigger
from shop.Item import Item
from shop.ItemGroup import ItemGroup
from shop.ItemType import ItemType

class SlapBoost(Item):

    def __init__(
        self,
        cost: int|None
    ):
        defaultcost = 120
        
        if cost is None:
            cost = defaultcost
        
        super().__init__(
            name = 'Massive Bonking Hammer',
            type = ItemType.SLAP_BOOST,
            group = ItemGroup.VALUE_MODIFIER,
            description = 'For when someone has been extra horny. Powers up your next slap by 5x.',
            emoji = '🔨',
            cost = cost,
            value = 5,
            view_class = None,
            allow_amount = False,
            base_amount = 1,
            max_amount = None,
            trigger = [ItemTrigger.SLAP]
        )

            