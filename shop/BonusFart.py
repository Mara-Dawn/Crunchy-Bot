from datalayer.UserInteraction import UserInteraction
from shop.ItemGroup import ItemGroup
from shop.ItemType import ItemType
from shop.TriggerItem import TriggerItem

class BonusFart(TriggerItem):

    def __init__(
        self,
        cost: int|None
    ):
        name = 'Bonus Fart'
        type = ItemType.BONUS_FART
        group = ItemGroup.BONUS_ATTEMPT
        description = 'Allows you to continue farting on a jailed person after using your guaranteed one.'
        defaultcost = 100
        emoji = '😂'
        trigger = [UserInteraction.FART]
        value = True 
        
        if cost is None:
            cost = defaultcost
            
        super().__init__(name, type, group, description, emoji, cost, trigger, value)