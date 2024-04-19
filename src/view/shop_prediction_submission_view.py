import discord
from control.controller import Controller
from items.item import Item
from view.shop_response_view import (
    CancelButton,
    ShopResponseView,
    SubmissionInputButton,
)


class ShopPredictionSubmissionView(ShopResponseView):

    def __init__(
        self,
        controller: Controller,
        interaction: discord.Interaction,
        item: Item,
        parent_id: int,
    ):
        super().__init__(controller, interaction, item, parent_id)

        self.submission_button = SubmissionInputButton()
        self.cancel_button = CancelButton()

        self.refresh_elements()

    async def submit(self, interaction: discord.Interaction):
        pass
