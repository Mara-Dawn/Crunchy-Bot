import discord

from control.view import ShopResponseViewController
from items import Item

# pylint: disable-next=unused-import,W0614,W0401
from view.shop_response_view import *


class ShopColorSelectView(ShopResponseView):

    def __init__(
        self,
        controller: ShopResponseViewController,
        interaction: discord.Interaction,
        item: Item,
    ):
        super().__init__(controller, interaction, item)

        self.selected_color = self.controller.get_custom_color(
            interaction.guild_id, interaction.user.id
        )

        self.amount_select = AmountInput(suffix=" Week(s)")
        self.color_input_button = ColorInputButton(self.selected_color)
        self.confirm_button = ConfirmButton()
        self.cancel_button = CancelButton()

        self.refresh_elements()

    async def submit(self, interaction: discord.Interaction):
        self.controller.submit_generic_view(interaction, self)
