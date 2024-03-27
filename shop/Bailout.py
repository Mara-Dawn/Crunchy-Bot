from shop.IsntantItem import InstantItem
from shop.ItemGroup import ItemGroup
from shop.ItemType import ItemType
class Bailout(InstantItem):

    def __init__(
        self,
        cost: str|int|None
    ):
        self.name = 'Bribe the Mods'
        type = ItemType.BAILOUT
        group = ItemGroup.IMMEDIATE_USE
        self.description = 'Pay off the mods to let you out of jail early.'
        defaultcost = 1500
        emoji = '🗿'
        view = 'ShopConfirmView'
        
        if cost is None:
            cost = defaultcost
        
        super().__init__(self.name, type, group, self.description, emoji, cost, view)