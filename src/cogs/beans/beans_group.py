from bot import CrunchyBot
from control.controller import Controller
from control.event_manager import EventManager
from control.item_manager import ItemManager
from control.logger import BotLogger
from control.prediction_manager import PredictionManager
from control.role_manager import RoleManager
from control.settings_manager import SettingsManager
from datalayer.database import Database
from discord.ext import commands


class BeansGroup(commands.GroupCog):

    def __init__(self, bot: CrunchyBot) -> None:
        self.bot = bot
        self.logger: BotLogger = bot.logger
        self.database: Database = bot.database
        self.controller: Controller = bot.controller
        self.item_manager: ItemManager = self.controller.get_service(ItemManager)
        self.event_manager: EventManager = self.controller.get_service(EventManager)
        self.role_manager: RoleManager = self.controller.get_service(RoleManager)
        self.prediction_manager: PredictionManager = self.controller.get_service(
            PredictionManager
        )
        self.settings_manager: SettingsManager = self.controller.get_service(
            SettingsManager
        )
