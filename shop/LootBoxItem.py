from shop.IsntantItem import InstantItem
from shop.ItemGroup import ItemGroup
from shop.ItemType import ItemType

class LootBoxItem(InstantItem):

    def __init__(
        self,
        cost: int|None
    ):
        self.name = 'Random Treasure Chest'
        type = ItemType.LOOTBOX
        group = ItemGroup.LOOTBOX
        self.description = 'No need to wait for loot box drops, just buy your own!'
        defaultcost = 150
        emoji = '🧰'
        view = 'LootBoxMenu'
        value = None
        
        if cost is None:
            cost = defaultcost
        
        super().__init__(self.name, type, group, self.description, emoji, cost, view, value)