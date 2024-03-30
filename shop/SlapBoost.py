from datalayer.ItemTrigger import ItemTrigger
from shop.ItemGroup import ItemGroup
from shop.ItemType import ItemType
from shop.TriggerItem import TriggerItem

class SlapBoost(TriggerItem):

    def __init__(
        self,
        cost: int|None
    ):
        name = 'Massive Bonking Hammer'
        type = ItemType.SLAP_BOOST
        group = ItemGroup.VALUE_MODIFIER
        description = 'For when someone has been extra horny. Powers up your next slap by 5x.'
        defaultcost = 120
        emoji = '🔨'
        trigger = [ItemTrigger.SLAP]
        value = 5
        
        if cost is None:
            cost = defaultcost
            
        super().__init__(name, type, group, description, emoji, cost, trigger, value)

            