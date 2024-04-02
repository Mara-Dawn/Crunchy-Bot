from shop.IsntantItem import InstantItem
from shop.ItemGroup import ItemGroup
from shop.ItemType import ItemType

class Release(InstantItem):

    def __init__(
        self,
        cost: int|None
    ):
        self.name = 'Get out of Jail Fart'
        type = ItemType.RELEASE
        group = ItemGroup.IMMEDIATE_USE
        self.description = 'Due to dietary advancements your farts can now help a friend out of jail for one time only.'
        defaultcost = 1000
        emoji = '🔑'
        view = 'ShopUserSelectView'
        value = None
        
        if cost is None:
            cost = defaultcost
        
        super().__init__(self.name, type, group, self.description, emoji, cost, view, value)