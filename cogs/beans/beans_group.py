from discord.ext import commands
from bot import CrunchyBot
from datalayer import Database
from control import (
    BotLogger,
    BotSettings,
    Controller,
    RoleManager,
    EventManager,
    ItemManager,
)


class BeansGroup(commands.GroupCog):

    def __init__(self, bot: CrunchyBot) -> None:
        self.bot = bot
        self.logger: BotLogger = bot.logger
        self.settings: BotSettings = bot.settings
        self.database: Database = bot.database
        self.event_manager: EventManager = bot.event_manager
        self.role_manager: RoleManager = bot.role_manager
        self.item_manager: ItemManager = bot.item_manager
        self.controller: Controller = bot.controller
