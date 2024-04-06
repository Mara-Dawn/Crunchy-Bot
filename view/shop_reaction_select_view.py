import discord

from control.controller import Controller
from events.types import UIEventType
from events.ui_event import UIEvent
from items.item import Item
from view.shop_response_view import (
    AmountInput,
    CancelButton,
    ConfirmButton,
    ReactionInputButton,
    ShopResponseView,
    UserPicker,
)
from view.types import EmojiType


class ShopReactionSelectView(ShopResponseView):

    def __init__(
        self,
        controller: Controller,
        interaction: discord.Interaction,
        item: Item,
        parent_id: int,
    ):
        super().__init__(controller, interaction, item, parent_id)

        _, default_emoji = self.controller.database.get_bully_react(
            interaction.guild_id, interaction.user.id
        )

        self.selected_emoji: discord.Emoji | str = default_emoji
        self.selected_emoji_type: EmojiType = (
            EmojiType.DEFAULT if isinstance(default_emoji, str) else EmojiType.CUSTOM
        )

        self.user_select = UserPicker()
        self.amount_select = AmountInput(suffix=" x 10 Reactions")
        self.reaction_input_button = ReactionInputButton()
        self.confirm_button = ConfirmButton()
        self.cancel_button = CancelButton()

        self.controller_class = "ShopResponseViewController"
        self.controller_module = "shop_response_view_controller"
        self.refresh_elements()

    async def submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        data = self.get_data()
        event = UIEvent(
            UIEventType.SHOP_RESPONSE_REACTION_SUBMIT,
            (interaction, data),
            self.parent_id,
        )
        await self.controller.dispatch_ui_event(event)
