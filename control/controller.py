from typing import List, Type
from discord.ext import commands
from control import (
    BotLogger,
    BotSettings,
    Service,
)
from control.view import ViewController
from datalayer import Database
from events import UIEvent, BotEvent


class Controller:

    def __init__(
        self,
        bot: commands.Bot,
        logger: BotLogger,
        database: Database,
        settings: BotSettings,
    ):
        self.bot = bot
        self.logger = logger
        self.database = database
        self.settings = settings

        self.services: List[Service] = []
        self.view_controllers: List[ViewController] = []

    def register_service(self, service: Service):
        self.services.append(service)

    def register_view_controller(self, view_controller: ViewController):
        self.view_controllers.append(view_controller)

    async def dispatch_event(self, event: BotEvent):
        for service in self.services:
            await service.listen_for_event(event)
        for view_controller in self.view_controllers:
            await view_controller.listen_for_event(event)

    async def dispatch_ui_event(self, event: UIEvent):
        for view_controller in self.view_controllers:
            await view_controller.listen_for_ui_event(event)

    def get_view_controller(self, controller: Type[ViewController]) -> ViewController:
        for view_controller in self.view_controllers:
            if isinstance(controller, view_controller):
                return view_controller

        new_controller = controller(self.bot)
        self.view_controllers.append(new_controller)
        return new_controller
