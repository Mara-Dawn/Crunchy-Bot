import discord

from items import Item

# pylint: disable-next=unused-import,W0614,W0401
from view.shop_response_view import *


class ShopUserSelectView(ShopResponseView):

    def __init__(
        self,
        controller: ShopResponseViewController,
        interaction: discord.Interaction,
        item: Item,
    ):
        super().__init__(controller, interaction, item)

        self.user_select = UserPicker()
        self.confirm_button = ConfirmButton()
        self.cancel_button = CancelButton()

        self.refresh_elements()

    async def submit(self, interaction: discord.Interaction):
        self.controller.submit_user_view(interaction, self)
