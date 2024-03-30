import datetime
from typing import Any, Dict, List

from datalayer.ItemTrigger import ItemTrigger
from events.EventManager import EventManager
from shop.Item import Item
from shop.ItemGroup import ItemGroup
from shop.ItemType import ItemType

class TriggerItem(Item):

    def __init__(
        self,
        name: str, 
        type: ItemType,
        group: ItemGroup,
        description: str,
        emoji: str,
        cost: int,
        trigger: List[ItemTrigger],
        value: Any,
        base_amount: int = 1,
        max_amount: int = None
    ):
        self.trigger = trigger
        self.value = value
        super().__init__(name, type, group, description, emoji, cost, base_amount=base_amount, max_amount=max_amount)

    def activated(self, action: ItemTrigger):
        return action in self.trigger
    
    def use(self, event_manager: EventManager, guild_id: int, member_id: int, amount: int = 1):
        event_manager.dispatch_inventory_event(
            datetime.datetime.now(), 
            guild_id,
            member_id,
            self.get_type(),
            0,
            -amount
        )
        
        return self.value
        
            