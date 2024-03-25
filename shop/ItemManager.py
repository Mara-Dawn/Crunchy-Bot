from discord.ext import commands
from BotLogger import BotLogger
from BotSettings import BotSettings
from shop.Item import Item
from shop.ItemType import ItemType

from shop.FartBoost import FartBoost
from shop.FartCrit import FartCrit

class ItemManager():

    def __init__(self, bot: commands.Bot, settings: BotSettings, logger: BotLogger):
        self.bot = bot
        self.settings = settings
        self.logger = logger
        self.log_name = "Shop"
        
    def get_item(self, guild_id: int, type: ItemType) -> Item:
        
        item = globals()[type]
        instance = item(self.settings.get_shop_item_price(guild_id, type))
        
        return instance