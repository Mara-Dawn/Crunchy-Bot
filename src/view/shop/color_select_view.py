import discord
from control.controller import Controller
from events.types import UIEventType
from events.ui_event import UIEvent
from items.item import Item
from view.shop.response_view import (
    AmountInput,
    CancelButton,
    ColorInputButton,
    ConfirmButton,
    ShopResponseView,
)


class ShopColorSelectView(ShopResponseView):

    def __init__(
        self,
        controller: Controller,
        interaction: discord.Interaction,
        item: Item,
        parent_id: int,
    ):
        super().__init__(controller, interaction, item, parent_id)

        self.selected_color = None
        self.amount_select = AmountInput(suffix=" Week(s)")
        self.color_input_button = ColorInputButton(None)
        self.confirm_button = ConfirmButton()
        self.cancel_button = CancelButton()
        self.refresh_elements()

    async def init(self):
        self.selected_color = await self.controller.database.get_custom_color(
            self.guild_id, self.member_id
        )
        self.color_input_button = ColorInputButton(self.selected_color)

    async def submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        data = self.get_data()
        event = UIEvent(
            UIEventType.SHOP_RESPONSE_COLOR_SUBMIT,
            (interaction, data),
            self.parent_id,
        )
        await self.controller.dispatch_ui_event(event)
