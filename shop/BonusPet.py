from datalayer.UserInteraction import UserInteraction
from shop.ItemGroup import ItemGroup
from shop.ItemType import ItemType
from shop.TriggerItem import TriggerItem

class BonusPet(TriggerItem):

    def __init__(
        self,
        cost: int|None
    ):
        name = 'Bonus Pet'
        type = ItemType.BONUS_PET
        group = ItemGroup.BONUS_ATTEMPT
        description = 'Allows you to continue giving pets to a jailed person after using your guaranteed one.'
        defaultcost = 35
        emoji = '🥰'
        trigger = [UserInteraction.PET]
        value = True
        
        if cost is None:
            cost = defaultcost
            
        super().__init__(name, type, group, description, emoji, cost, trigger, value)
            