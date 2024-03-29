from datalayer.UserInteraction import UserInteraction
from shop.ItemGroup import ItemGroup
from shop.ItemType import ItemType
from shop.TriggerItem import TriggerItem

class PetBoost(TriggerItem):

    def __init__(
        self,
        cost: int|None
    ):
        name = 'Big Mama Bear Hug'
        type = ItemType.PET_BOOST
        group = ItemGroup.VALUE_MODIFIER
        description = 'When a normal pet just isnt enough. Powers up your next pet by 5x.'
        defaultcost = 120
        emoji = '🧸'
        trigger = [UserInteraction.PET]
        value = 5
        
        if cost is None:
            cost = defaultcost
            
        super().__init__(name, type, group, description, emoji, cost, trigger, value)

            