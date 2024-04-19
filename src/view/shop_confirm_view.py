import discord
from control.controller import Controller
from events.types import UIEventType
from events.ui_event import UIEvent
from items.item import Item
from view.shop_response_view import (
    AmountInput,
    CancelButton,
    ConfirmButton,
    ShopResponseView,
)


class ShopConfirmView(ShopResponseView):  # noqa: F405

    def __init__(
        self,
        controller: Controller,
        interaction: discord.Interaction,
        item: Item,
        parent_id: int,
    ):
        super().__init__(controller, interaction, item, parent_id)

        self.amount_select = AmountInput()
        self.confirm_button = ConfirmButton()
        self.cancel_button = CancelButton()

        self.refresh_elements()

    async def submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        data = self.get_data()
        event = UIEvent(
            UIEventType.SHOP_RESPONSE_CONFIRM_SUBMIT,
            (interaction, data),
            self.parent_id,
        )
        await self.controller.dispatch_ui_event(event)
