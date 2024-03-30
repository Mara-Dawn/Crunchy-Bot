from datalayer.ItemTrigger import ItemTrigger
from shop.ItemGroup import ItemGroup
from shop.ItemType import ItemType
from shop.TriggerItem import TriggerItem

class BonusSlap(TriggerItem):

    def __init__(
        self,
        cost: int|None
    ):
        name = 'Bonus Slap'
        type = ItemType.BONUS_SLAP
        group = ItemGroup.BONUS_ATTEMPT
        description = 'Allows you to continue slapping a jailed person after using your guaranteed one.'
        defaultcost = 35
        emoji = '✋'
        trigger = [ItemTrigger.SLAP]
        value = True
        
        if cost is None:
            cost = defaultcost
            
        super().__init__(name, type, group, description, emoji, cost, trigger, value)
            