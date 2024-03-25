import datetime
from typing import Any, Dict

from shop.Item import Item
from shop.ItemType import ItemType

class FartCrit(Item):

    def __init__(
        self,
        cost: int|None
    ):
        name = 'Critical Fart'
        type = ItemType.FART_CRIT
        description = 'Guarantees a crit on your next fart.'
        defaultcost = 60
        emoji = '🤢'
        
        if cost is None:
            cost = defaultcost
        
        super().__init__(name, type, description, emoji, cost)
    
        def handle() -> None:
            pass