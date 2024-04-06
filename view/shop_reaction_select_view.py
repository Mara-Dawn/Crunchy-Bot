import discord

from items import Item

# pylint: disable-next=unused-import,W0614,W0401
from view.shop_response_view import *


class ShopReactionSelectView(ShopResponseView):

    def __init__(
        self,
        controller: ShopResponseViewController,
        interaction: discord.Interaction,
        item: Item,
    ):
        super().__init__(controller, interaction, item)

        _, default_emoji = self.controller.get_bully_react(
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

        self.refresh_elements()

    async def submit(self, interaction: discord.Interaction):
        self.controller.submit_generic_view(interaction, self)
