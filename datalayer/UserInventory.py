from typing import Dict

from shop.ItemType import ItemType

class UserInventory():

    def __init__(
        self,
        guild_id: int,
        member: int,
        inventory: Dict[ItemType,int]
    ):
        self.guild_id = guild_id
        self.member = member
        self.inventory = inventory
    
    def get_guild_id(self) -> int:
        return self.guild_id
        
    def get_member_id(self) -> int:
        return self.member
    
    def get_inventory_items(self) -> Dict[ItemType,int]:
        return self.inventory
    
    def get_item_count(self, type: ItemType) -> int:
        if type not in self.inventory.keys():
            return 0
        return self.inventory[type]
        
        