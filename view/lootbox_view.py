import discord

from control.view import LootBoxViewController
from events import UIEvent
from view import ViewMenu


class LootBoxView(ViewMenu):

    def __init__(self, controller: LootBoxViewController, owner_id: int = None):
        super().__init__(timeout=None)
        self.add_item(ClaimButton())
        self.controller = controller
        self.owner_id = owner_id

        self.controller.register_view(self)

    async def claim(self, interaction: discord.Interaction):
        await self.controller.handle_lootbox_claim(interaction, self, self.owner_id)

    def listen_for_ui_event(self, event: UIEvent):
        pass


class ClaimButton(discord.ui.Button):

    def __init__(self):
        super().__init__(label="Mine!", style=discord.ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        view: LootBoxView = self.view

        await view.claim(interaction)
