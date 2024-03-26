import datetime
from typing import Any, List
from discord.ext import commands
from BotLogger import BotLogger
from BotSettings import BotSettings
from datalayer.Database import Database
from datalayer.UserInteraction import UserInteraction
from events.EventManager import EventManager
from shop.Item import Item
from shop.ItemGroup import ItemGroup
from shop.ItemType import ItemType

from shop.FartBoost import FartBoost
from shop.FartCrit import FartCrit

class ItemManager():

    def __init__(self, bot: commands.Bot, settings: BotSettings, database: Database, event_manager: EventManager, logger: BotLogger):
        self.bot = bot
        self.settings = settings
        self.database = database
        self.event_manager = event_manager
        self.logger = logger
        self.log_name = "Shop"
        
    def get_item(self, guild_id: int, type: ItemType) -> Item:
        
        item = globals()[type]
        instance = item(self.settings.get_shop_item_price(guild_id, type))
        
        return instance
    
    def get_items(self, guild_id: int) -> List[Item]:
        items = [x.value for x in ItemType]
        output = []
        for item_type in items:
            output.append(self.get_item(guild_id, item_type))
            
        return output
    
    
    
    def get_user_items_activated(self, guild_id: int, user_id: int, group: ItemGroup, action: UserInteraction) -> List[Item]:
        inventory = self.database.get_inventory_by_user(guild_id, user_id)
        inventory_items = inventory.get_inventory_items()
        
        output = []
        
        for item_type, count in inventory_items.items():
            
            item = self.get_item(guild_id, item_type)
            
            if item.get_group() != group:
                continue
            
            if not item.activated(action):
                continue
            
            output.append(item)
        
        return output
    