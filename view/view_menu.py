from abc import ABC, abstractmethod
import discord
from events.ui_event import UIEvent


class ViewMenu(discord.ui.View, ABC):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @abstractmethod
    async def listen_for_ui_event(self, event: UIEvent):
        pass
