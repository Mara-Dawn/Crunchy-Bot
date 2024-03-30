from typing import Any, List
from discord.ext import commands
from BotLogger import BotLogger
from BotSettings import BotSettings
from datalayer.Database import Database
from datalayer.ItemTrigger import ItemTrigger
from datalayer.UserInteraction import UserInteraction
from events.EventManager import EventManager
from shop.Item import Item
from shop.ItemType import ItemType
from shop.TriggerItem import TriggerItem

# needed for global access
from shop.AutoCrit import AutoCrit
from shop.FartBoost import FartBoost
from shop.PetBoost import PetBoost
from shop.SlapBoost import SlapBoost
from shop.BonusFart import BonusFart
from shop.BonusPet import BonusPet
from shop.BonusSlap import BonusSlap
from shop.GigaFart import GigaFart
from shop.FartStabilizer import FartStabilizer
from shop.Fartvantage import Fartvantage
from shop.FartProtection import FartProtection
from shop.LotteryTicket import LotteryTicket

from shop.Arrest import Arrest
from shop.Release import Release
from shop.Bailout import Bailout
from shop.JailReduction import JailReduction


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
    
    def get_trigger_item(self, guild_id: int, type: ItemType) -> TriggerItem:
        return self.get_item(guild_id, type)
    
    def get_items(self, guild_id: int) -> List[Item]:
        items = [x.value for x in ItemType]
        output = []
        for item_type in items:
            output.append(self.get_item(guild_id, item_type))
            
        return output
    
    def get_user_items_activated_by_interaction(self, guild_id: int, user_id: int, action: UserInteraction) -> List[TriggerItem]:
        trigger = None
        
        match action:
            case UserInteraction.FART:
                trigger = ItemTrigger.FART
            case UserInteraction.SLAP:
                trigger = ItemTrigger.SLAP
            case UserInteraction.PET:
                trigger = ItemTrigger.PET
        
        return self.get_user_items_activated(guild_id, user_id, trigger)
    
    
    def get_user_items_activated(self, guild_id: int, user_id: int, action: ItemTrigger) -> List[TriggerItem]:
        inventory = self.database.get_inventory_by_user(guild_id, user_id)
        inventory_items = inventory.get_inventory_items()
        
        output = []
        
        for item_type, count in inventory_items.items():
            
            item = self.get_item(guild_id, item_type)
            
            if not item.activated(action):
                continue
            
            output.append(item)
        
        return output
    