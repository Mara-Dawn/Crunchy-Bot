import discord

from control.controller import Controller
from events.types import UIEventType
from events.ui_event import UIEvent
from items.item import Item
from view.shop_response_view import (
    CancelButton,
    ConfirmButton,
    ShopResponseView,
    UserPicker,
)


class ShopUserSelectView(ShopResponseView):

    def __init__(
        self,
        controller: Controller,
        interaction: discord.Interaction,
        item: Item,
    ):
        super().__init__(controller, interaction, item)

        self.user_select = UserPicker()
        self.confirm_button = ConfirmButton()
        self.cancel_button = CancelButton()

        self.refresh_elements()

    async def submit(self, interaction: discord.Interaction):
        data = self.get_data()
        event = UIEvent(
            UIEventType.SHOP_RESPONSE_USER_SUBMIT,
            (interaction, data),
            self.parent_id,
        )
        await self.controller.dispatch_ui_event(event)
