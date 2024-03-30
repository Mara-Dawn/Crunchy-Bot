from datalayer.ItemTrigger import ItemTrigger
from shop.ItemGroup import ItemGroup
from shop.ItemType import ItemType
from shop.TriggerItem import TriggerItem

class Fartvantage(TriggerItem):

    def __init__(
        self,
        cost: int|None
    ):
        name = 'Fast Food Binge'
        type = ItemType.FARTVANTAGE
        group = ItemGroup.ADVANTAGE
        description = 'Couldn\'t hold back again, hm? Better go empty your bowels on some poor loser. Rolls your next fart twice and takes the better result.'
        defaultcost = 69
        emoji = '🍔'
        trigger = [ItemTrigger.FART]
        value = 2
        
        if cost is None:
            cost = defaultcost
            
        super().__init__(name, type, group, description, emoji, cost, trigger, value)