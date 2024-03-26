from datalayer.UserInteraction import UserInteraction
from shop.ItemGroup import ItemGroup
from shop.ItemType import ItemType
from shop.TriggerItem import TriggerItem

class AutoCrit(TriggerItem):

    def __init__(
        self,
        cost: int|None
    ):
        name = 'Magic Beans'
        type = ItemType.AUTO_CRIT
        group = ItemGroup.AUTO_CRIT
        description = 'Let these rainbow colored little beans guide your next slap, pet or fart to a guaranteed critical hit.'
        defaultcost = 100
        emoji = '💥'
        trigger = [UserInteraction.FART, UserInteraction.PET, UserInteraction.SLAP]
        value = True 
        
        if cost is None:
            cost = defaultcost
        
        super().__init__(name, type, group, description, emoji, cost, trigger, value)
        
            