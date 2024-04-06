from typing import List
import discord
from discord.ext import commands
from control.event_manager import EventManager
from control.item_manager import ItemManager
from control.logger import BotLogger
from control.role_manager import RoleManager
from control.settings import SettingsManager
from control.service import Service
from datalayer.database import Database
from events.ui_event import UIEvent
from view.view_menu import ViewMenu


class ViewController(Service):

    def __init__(
        self,
        bot: commands.Bot,
        logger: BotLogger,
        settings: SettingsManager,
        database: Database,
        event_manager: EventManager,
        role_manager: RoleManager,
        item_manager: ItemManager,
    ):
        super().__init__()
        self.bot = bot
        self.logger = logger
        self.settings = settings
        self.database = database
        self.event_manager = event_manager
        self.role_manager = role_manager
        self.item_manager = item_manager
        self.views: List[ViewMenu] = []

    def register_view(self, view: ViewMenu) -> None:
        self.views.append(view)

    def detach_view(self, view: ViewMenu) -> None:
        self.views.remove(view)

    async def listen_for_ui_event(self, event: UIEvent) -> None:
        for view in self.views:
            await view.listen_for_ui_event(event)

    async def interaction_check(
        self, interaction: discord.Interaction, user_id: int
    ) -> bool:
        if interaction.user.id == user_id:
            return True
        else:
            await interaction.response.send_message(
                "Only the author of the command can perform this action.",
                ephemeral=True,
            )
            return False
