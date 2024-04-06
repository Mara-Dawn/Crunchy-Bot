from discord.ext import commands

from control.logger import BotLogger
from control.service import Service
from datalayer.database import Database
from events.ui_event import UIEvent


class ViewController(Service):

    def __init__(
        self,
        bot: commands.Bot,
        logger: BotLogger,
        database: Database,
    ):
        super().__init__()
        self.bot = bot
        self.logger = logger
        self.database = database

    async def listen_for_ui_event(self, event: UIEvent) -> None:
        pass
