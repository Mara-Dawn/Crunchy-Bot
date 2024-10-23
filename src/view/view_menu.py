import sys
from abc import ABC, abstractmethod
from typing import Any

import discord

from control.types import ControllerType
from error import ErrorHandler
from events.ui_event import UIEvent


class ViewMenu(discord.ui.View, ABC):

    class_counter = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = ViewMenu.class_counter
        self.member_id = None
        self.controller_types: list[ControllerType] = None
        self.message: discord.Message = None
        self.guild_level: int = 1
        ViewMenu.class_counter += 1

    @abstractmethod
    async def listen_for_ui_event(self, event: UIEvent):
        pass

    def set_message(self, message: discord.Message):
        self.message = message

    async def on_error(
        self,
        interaction: discord.Interaction,
        error: Exception,
        item: discord.ui.Item[Any],
        /,
    ) -> None:
        error_handler = ErrorHandler(interaction.client)
        await error_handler.post_error(sys.exc_info()[1], interaction)
        return await super().on_error(interaction, error, item)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.member_id:
            return True
        else:
            await interaction.response.send_message(
                "You dont have permission to use this.",
                ephemeral=True,
            )
            return False
