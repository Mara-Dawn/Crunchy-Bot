import discord
from items.item import Item

# pylint: disable-next=unused-import,W0614,W0401
from view.shop_response_view import *


class ShopConfirmView(ShopResponseView):

    def __init__(
        self,
        controller: ShopResponseViewController,
        interaction: discord.Interaction,
        item: Item,
    ):
        super().__init__(controller, interaction, item)

        self.amount_select = AmountInput()
        self.confirm_button = ConfirmButton()
        self.cancel_button = CancelButton()

        self.refresh_elements()

    async def submit(self, interaction: discord.Interaction):
        self.controller.submit_confirm_view(interaction, self)
