import datetime
from typing import Any, Dict

from shop.Item import Item
from shop.ItemType import ItemType

class FartBoost(Item):

    def __init__(
        self,
        cost: int|None
    ):
        name = 'Fart Boost x3'
        type = ItemType.FART_BOOST
        description = 'Multiplies the power of your next fart by 3.'
        defaultcost = 100
        
        if cost is None:
            cost = defaultcost
        
        super().__init__(name, type , description, cost)
    
        def handle() -> None:
            pass