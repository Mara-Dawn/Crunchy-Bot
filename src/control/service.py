from abc import ABC, abstractmethod

from discord.ext import commands
from events.bot_event import BotEvent

from control.database_manager import DatabaseManager
from control.logger import BotLogger


class Service(ABC):

    def __init__(
        self,
        bot: commands.Bot,
        logger: BotLogger,
        database: DatabaseManager,
    ):
        self.controller = None
        self.bot = bot
        self.logger = logger
        self.database = database

    @abstractmethod
    async def listen_for_event(self, event: BotEvent) -> None:
        pass
