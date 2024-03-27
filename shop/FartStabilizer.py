from datalayer.UserInteraction import UserInteraction
from shop.ItemGroup import ItemGroup
from shop.ItemType import ItemType
from shop.TriggerItem import TriggerItem

class FartStabilizer(TriggerItem):

    def __init__(
        self,
        cost: int|None
    ):
        name = 'Ass ACOG'
        type = ItemType.FART_STABILIZER
        group = ItemGroup.STABILIZER
        description = 'Stabilizes your aim and increases your rectal precision. Your next fart cannot roll below 0.'
        defaultcost = 45
        emoji = '🔭'
        trigger = [UserInteraction.FART]
        value = 10
        
        if cost is None:
            cost = defaultcost
            
        super().__init__(name, type, group, description, emoji, cost, trigger, value)