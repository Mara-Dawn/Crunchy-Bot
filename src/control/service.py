from abc import ABC, abstractmethod

from datalayer.database import Database
from discord.ext import commands
from events.bot_event import BotEvent

from control.logger import BotLogger


class Service(ABC):

    def __init__(
        self,
        bot: commands.Bot,
        logger: BotLogger,
        database: Database,
    ):
        self.controller = None
        self.bot = bot
        self.logger = logger
        self.database = database

    @abstractmethod
    async def listen_for_event(self, event: BotEvent) -> None:
        pass
