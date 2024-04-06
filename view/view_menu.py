from abc import ABC, abstractmethod

import discord

from events.ui_event import UIEvent


class ViewMenu(discord.ui.View, ABC):

    class_counter = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = ViewMenu.class_counter
        ViewMenu.class_counter += 1

    @abstractmethod
    async def listen_for_ui_event(self, event: UIEvent):
        pass

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
