import discord

from discord.ext import commands
from typing import *
from BotLogger import BotLogger
from BotSettings import BotSettings
from CrunchyBot import CrunchyBot
from RoleManager import RoleManager
from datalayer.Database import Database
from events.EventManager import EventManager
from shop.ItemManager import ItemManager

class BeansGroup(commands.GroupCog):
    
    def __init__(self, bot: CrunchyBot):
        self.bot = bot
        self.logger: BotLogger = bot.logger
        self.settings: BotSettings = bot.settings
        self.database: Database = bot.database
        self.event_manager: EventManager = bot.event_manager
        self.role_manager: RoleManager = bot.role_manager
        self.item_manager: ItemManager = bot.item_manager