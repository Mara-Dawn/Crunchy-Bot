import datetime
import random
import discord

from typing import Any, List
from discord.ext import commands
from BotLogger import BotLogger
from BotSettings import BotSettings
from datalayer.Database import Database
from datalayer.ItemTrigger import ItemTrigger
from datalayer.LootBox import LootBox
from datalayer.UserInteraction import UserInteraction
from events.EventManager import EventManager
from events.LootBoxEventType import LootBoxEventType
from shop.Item import Item
from shop.ItemType import ItemType
from shop.TriggerItem import TriggerItem
from view.LootBoxMenu import LootBoxMenu

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
    
    def create_loot_box(self, guild_id: int) -> LootBox:
        item_pool = [
            ItemType.AUTO_CRIT,
            ItemType.FART_BOOST,
            ItemType.PET_BOOST,
            ItemType.SLAP_BOOST,
            ItemType.BONUS_FART,
            ItemType.BONUS_PET,
            ItemType.BONUS_SLAP,
            ItemType.GIGA_FART,
            ItemType.FART_STABILIZER,
            ItemType.FARTVANTAGE,
            ItemType.FARTVANTAGE,
            ItemType.FARTVANTAGE
        ]
        
        mimic_chance = 0.1
        weights = [self.get_trigger_item(guild_id, x).get_cost() for x in item_pool]
        chance_for_item = self.settings.get_setting(guild_id, BotSettings.BEANS_SUBSETTINGS_KEY, BotSettings.BEANS_LOOTBOX_RARE_CHANCE_KEY)
        random_item = None
        roll = random.random()
        if roll < chance_for_item:
            random_item = random.choices(item_pool, weights=weights)[0]
        
        min_beans = self.settings.get_setting(guild_id, BotSettings.BEANS_SUBSETTINGS_KEY, BotSettings.BEANS_LOOTBOX_MIN_BEANS_KEY)
        max_beans = self.settings.get_setting(guild_id, BotSettings.BEANS_SUBSETTINGS_KEY, BotSettings.BEANS_LOOTBOX_MAX_BEANS_KEY)
        
        beans = random.randint(min_beans,max_beans)
        
        if random_item is None and roll > 1-mimic_chance:
            beans = -beans
        elif random_item is None and random.random() < chance_for_item:
            beans = random.randint(min_beans*10,max_beans*10)
        
        return LootBox(guild_id, random_item, beans)
    
    async def drop_loot_box(self, guild: discord.Guild, channel_id: int):
        log_message = f'Loot box was dropped in {guild.name}.'
        self.logger.log(guild.id, log_message, cog="Beans")
        
        loot_box = self.create_loot_box(guild.id)
        
        title = "A Random Treasure has Appeared"
        description = "Quick, claim it before anyone else does!"
        embed = discord.Embed(title=title, description=description, color=discord.Colour.purple()) 
        embed.set_image(url="attachment://treasure_closed.jpg")
        item = None
        if loot_box.get_item_type() is not None:
            item = self.get_item(guild.id, loot_box.get_item_type())
        view = LootBoxMenu(self.event_manager, self.database, self.logger, item)
        
        treasure_close_img = discord.File("./img/treasure_closed.jpg", "treasure_closed.jpg")
        
        channel = guild.get_channel(channel_id)
        
        message = await channel.send("",embed=embed, view=view, files=[treasure_close_img])
        
        loot_box.set_message_id(message.id)
        loot_box_id = self.database.log_lootbox(loot_box)
        
        self.event_manager.dispatch_loot_box_event(
            datetime.datetime.now(), 
            guild.id,
            loot_box_id,
            self.bot.user.id,
            LootBoxEventType.DROP
        )
    
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
    