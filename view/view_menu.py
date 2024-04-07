from abc import ABC, abstractmethod

import discord

from control.types import ControllerType
from events.ui_event import UIEvent


class ViewMenu(discord.ui.View, ABC):

    class_counter = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = ViewMenu.class_counter
        self.member_id = None
        self.controller_type: ControllerType = None
        ViewMenu.class_counter += 1

    @abstractmethod
    async def listen_for_ui_event(self, event: UIEvent):
        pass

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.member_id:
            return True
        else:
            await interaction.response.send_message(
                "Only the author of the command can perform this action.",
                ephemeral=True,
            )
            return False
