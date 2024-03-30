from datalayer.ItemTrigger import ItemTrigger
from shop.ItemGroup import ItemGroup
from shop.ItemType import ItemType
from shop.TriggerItem import TriggerItem

class FartBoost(TriggerItem):

    def __init__(
        self,
        cost: int|None
    ):
        name = 'UK Breakfast Beans'
        type = ItemType.FART_BOOST
        group = ItemGroup.VALUE_MODIFIER
        description = 'Extremely dangerous, multiplies the power of your next fart by 3.'
        defaultcost = 150
        emoji = '🤢'
        trigger = [ItemTrigger.FART]
        value = 3
        
        if cost is None:
            cost = defaultcost
            
        super().__init__(name, type, group, description, emoji, cost, trigger, value)