from datalayer.UserInteraction import UserInteraction
from shop.ItemGroup import ItemGroup
from shop.ItemType import ItemType
from shop.TriggerItem import TriggerItem

class FartProtection(TriggerItem):

    def __init__(
        self,
        cost: int|None
    ):
        name = 'Your Uncle\'s old Hazmat Suit'
        type = ItemType.FART_PROTECTION
        group = ItemGroup.PROTECTION
        description = 'According to him his grandpa took it from a dead guy in ww2. The next 5 interactions negatively affecting your jailtime will be reduced by 50%'
        defaultcost = 175
        emoji = '☣'
        trigger = [UserInteraction.FART]
        value = 0.5
        base_amount = 5
        
        if cost is None:
            cost = defaultcost
            
        super().__init__(name, type, group, description, emoji, cost, trigger, value, base_amount)