import discord
from control.controller import Controller
from events.types import UIEventType
from events.ui_event import UIEvent
from items.item import Item
from view.shop.response_view import (
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

        self.selected_emoji: discord.Emoji | str = None
        self.selected_emoji_type: EmojiType = None

        self.user_select = UserPicker()
        self.amount_select = AmountInput(suffix=" x 10 Reactions")
        self.reaction_input_button = ReactionInputButton()
        self.confirm_button = ConfirmButton()
        self.cancel_button = CancelButton()

        self.refresh_elements()

    async def init(self):
        _, default_emoji = await self.controller.database.get_bully_react(
            self.guild_id, self.member_id
        )
        self.selected_emoji: discord.Emoji | str = None
        self.selected_emoji_type: EmojiType = (
            EmojiType.DEFAULT if isinstance(default_emoji, str) else EmojiType.CUSTOM
        )
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
