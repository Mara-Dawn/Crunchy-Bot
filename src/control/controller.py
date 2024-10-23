import asyncio
import importlib

import discord
from discord.ext import commands

from control.logger import BotLogger
from control.service import Service
from control.types import ControllerModuleMap
from control.view.view_controller import ViewController
from datalayer.database import Database
from events.bot_event import BotEvent
from events.ui_event import UIEvent
from view.view_menu import ViewMenu


class Controller:

    def __init__(
        self,
        bot: commands.Bot,
        logger: BotLogger,
        database: Database,
    ):
        self.bot = bot
        self.logger = logger
        self.database = database

        self.services: list[Service] = []
        self.view_controllers: list[ViewController] = []
        self.views: list[ViewMenu] = []

    def register_view(self, view: ViewMenu):

        controller_types = view.controller_types

        for controller_type in controller_types:
            controller_type = controller_type.value
            controller_class = getattr(
                importlib.import_module(
                    "control.view." + ControllerModuleMap.get_module(controller_type)
                ),
                controller_type,
            )
            self.add_view_controller(controller_class)
        self.views.append(view)

    def detach_view(self, view: ViewMenu):
        if view in self.views:
            self.views.remove(view)

    def detach_view_by_id(self, view_id: int):
        for view in self.views:
            if view.id == view_id:
                self.views.remove(view)

    async def execute_garbage_collection(self):
        for view in self.views:
            if view.message is None:
                continue

            try:
                await asyncio.sleep(5)
                await view.message.edit()
            except (discord.NotFound, discord.HTTPException):
                if view in self.views:
                    self.views.remove(view)

    async def dispatch_event(self, event: BotEvent):
        tasks = []
        for service in self.services:
            tasks.append(asyncio.create_task(service.listen_for_event(event)))
        for view_controller in self.view_controllers:
            tasks.append(asyncio.create_task(view_controller.listen_for_event(event)))
        result = await asyncio.gather(*tasks, return_exceptions=True)

        for res in result:
            if isinstance(res, Exception):
                raise res

    async def dispatch_ui_event(self, event: UIEvent):
        tasks = []
        for view_controller in self.view_controllers:
            tasks.append(
                asyncio.create_task(view_controller.listen_for_ui_event(event))
            )
        for view in self.views:
            tasks.append(asyncio.create_task(view.listen_for_ui_event(event)))
        result = await asyncio.gather(*tasks, return_exceptions=True)

        for res in result:
            if isinstance(res, Exception):
                raise res

    def get_service(self, service_class: type[Service]) -> Service:
        for service in self.services:
            if isinstance(service, service_class):
                return service

        new_service = service_class(self.bot, self.logger, self.database, self)
        self.services.append(new_service)
        return new_service

    def get_view(self, id: int) -> ViewMenu:
        for view in self.views:
            if view.id == id:
                return view
        return None

    def add_view_controller(self, controller: type[ViewController]) -> ViewController:
        for view_controller in self.view_controllers:
            if isinstance(view_controller, controller):
                return

        new_controller = controller(self.bot, self.logger, self.database, self)
        self.view_controllers.append(new_controller)
