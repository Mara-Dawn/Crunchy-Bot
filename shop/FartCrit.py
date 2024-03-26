import datetime
from typing import Any, Dict

from datalayer.UserInteraction import UserInteraction
from events.EventManager import EventManager
from shop.Item import Item
from shop.ItemGroup import ItemGroup
from shop.ItemType import ItemType

class FartCrit(Item):

    def __init__(
        self,
        cost: int|None
    ):
        name = 'Critical Fart'
        type = ItemType.FART_CRIT
        group = ItemGroup.AUTO_CRIT
        description = 'Guarantees a crit on your next fart.'
        defaultcost = 60
        emoji = '🤢'
        self.trigger = UserInteraction.FART
        
        if cost is None:
            cost = defaultcost
        
        super().__init__(name, type, group, description, emoji, cost)

    def activated(self, action: UserInteraction):
        return  action == self.trigger
    
    def use(self, event_manager: EventManager, guild_id: int, member_id: int):
        event_manager.dispatch_inventory_event(
            datetime.datetime.now(), 
            guild_id,
            member_id,
            self.get_type(),
            0,
            -1
        )
        
        return 1
        
            