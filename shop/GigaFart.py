from datalayer.UserInteraction import UserInteraction
from shop.ItemGroup import ItemGroup
from shop.ItemType import ItemType
from shop.TriggerItem import TriggerItem

class GigaFart(TriggerItem):

    def __init__(
        self,
        cost: int|None
    ):
        name = 'Shady 4am Chinese Takeout'
        type = ItemType.GIGA_FART
        group = ItemGroup.VALUE_MODIFIER
        description = 'Works better than any laxative and boosts the pressure of your next fart by x10. Try not to hurt yoruself.'
        defaultcost = 500
        emoji = '💀'
        trigger = [UserInteraction.FART]
        value = 10
        
        if cost is None:
            cost = defaultcost
            
        super().__init__(name, type, group, description, emoji, cost, trigger, value)