import datetime
from typing import Any, Dict, List

from datalayer.UserInteraction import UserInteraction
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
        trigger: List[UserInteraction],
        value: Any
    ):
        self.trigger = trigger
        self.value = value
        super().__init__(name, type, group, description, emoji, cost)

    def activated(self, action: UserInteraction):
        return  action in self.trigger
    
    def use(self, event_manager: EventManager, guild_id: int, member_id: int):
        event_manager.dispatch_inventory_event(
            datetime.datetime.now(), 
            guild_id,
            member_id,
            self.get_type(),
            0,
            -1
        )
        
        return self.value
        
            