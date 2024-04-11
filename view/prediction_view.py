import contextlib

import discord

from control.controller import Controller
from control.types import ControllerType
from datalayer.prediction_stats import PredictionStats
from datalayer.types import PredictionState
from events.types import UIEventType
from events.ui_event import UIEvent
from view.prediction_embed import PredictionEmbed
from view.prediction_moderation_embed import PredictionModerationEmbed
from view.view_menu import ViewMenu


class PredictionView(ViewMenu):

    def __init__(
        self,
        controller: Controller,
        interaction: discord.Interaction,
        predictions: list[PredictionStats],
    ):
        super().__init__(timeout=300)
        self.controller = controller
        self.guild_name = interaction.guild.name
        self.member_id = interaction.user.id
        self.guild_id = interaction.guild_id
        self.current_page = 0

        self.filter: list[PredictionState] = [PredictionState.APPROVED]
        self.all_predictions = predictions
        self.predictions = []
        self.__filter_predictions()

        self.selected: int = None
        self.user_balance: int = 0
        self.user_bets: dict[int, tuple[int, int]] = {}

        self.item_count = len(self.predictions)
        self.page_count = int(self.item_count / PredictionEmbed.ITEMS_PER_PAGE) + (
            self.item_count % PredictionEmbed.ITEMS_PER_PAGE > 0
        )

        self.message = None
        self.disabled = False

        self.controller_type = ControllerType.PREDICTION_VIEW
        self.controller.register_view(self)
        self.refresh_elements()

    async def listen_for_ui_event(self, event: UIEvent):
        match event.type:
            case UIEventType.PREDICTION_USER_REFRESH:
                user_id = event.payload[0]
                if user_id != self.member_id:
                    return
                user_balance = event.payload[1]
                await self.refresh_ui(user_balance=user_balance)
            case UIEventType.PREDICTION_BET_REFRESH:
                user_id = event.payload[0]
                if user_id != self.member_id:
                    return
                user_bets = event.payload[1]
                user_balance = event.payload[2]
                await self.refresh_ui(
                    user_bets=user_bets, user_balance=user_balance, disabled=False
                )
            case UIEventType.PREDICTION_REFRESH_ALL:
                predictions = event.payload
                await self.refresh_ui(predictions=predictions)

        if event.view_id != self.id:
            return

        match event.type:
            case UIEventType.PREDICTION_REFRESH:
                predictions = event.payload
                await self.refresh_ui(predictions=predictions, disabled=False)
            case UIEventType.PREDICTION_DISABLE:
                await self.refresh_ui(disabled=event.payload)

    def __filter_predictions(self):
        self.predictions = [
            prediction
            for prediction in self.all_predictions
            if prediction.prediction.state == PredictionState.APPROVED
        ]
        self.item_count = len(self.predictions)
        self.page_count = int(
            self.item_count / PredictionModerationEmbed.ITEMS_PER_PAGE
        ) + (self.item_count % PredictionModerationEmbed.ITEMS_PER_PAGE > 0)

    def set_message(self, message: discord.Message):
        self.message = message

    async def select(self, interaction: discord.Interaction):
        await interaction.response.defer()

        if self.selected in self.user_bets:
            await interaction.followup.send(
                "You already placed a bet for this prediction.", ephemeral=True
            )
            return

        selected_stats = [
            prediction
            for prediction in self.predictions
            if prediction.prediction.id == self.selected
        ]

        selected = None
        if len(selected_stats) > 0:
            selected = selected_stats[0]

        event = UIEvent(
            UIEventType.PREDICTION_SELECT,
            (interaction, selected),
            self.id,
        )
        self.selected = None
        await self.controller.dispatch_ui_event(event)

    async def flip_page(self, interaction: discord.Interaction, right: bool = False):
        await interaction.response.defer()
        self.current_page = (self.current_page + (1 if right else -1)) % self.page_count
        self.selected = None
        event = UIEvent(
            UIEventType.PREDICTION_CHANGED,
            self.guild_id,
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    def refresh_elements(
        self,
        user_balance: int = None,
        disabled: bool = False,
    ):
        start = PredictionModerationEmbed.ITEMS_PER_PAGE * self.current_page
        end = min((start + PredictionModerationEmbed.ITEMS_PER_PAGE), self.item_count)
        page_display = f"Page {self.current_page + 1}/{max(1,self.page_count)}"

        self.disabled = disabled

        if user_balance is not None:
            self.user_balance = user_balance

        self.clear_items()
        if len(self.predictions) > 0:
            self.add_item(
                SelectDropdown(self.predictions[start:end], self.selected, disabled)
            )
        self.add_item(PageButton("<", False, disabled))
        self.add_item(SelectButton(disabled))
        self.add_item(PageButton(">", True, disabled))
        self.add_item(CurrentPageButton(page_display))
        self.add_item(BalanceButton(self.user_balance))

    async def refresh_ui(
        self,
        user_balance: int = None,
        user_bets: dict[int, tuple[int, int]] = None,
        predictions: list[PredictionStats] = None,
        disabled: bool = None,
    ):
        if disabled is None:
            disabled = self.disabled

        if user_bets is not None:
            self.user_bets = user_bets

        if predictions is not None:
            self.all_predictions = predictions

        self.__filter_predictions()

        self.refresh_elements(user_balance, disabled)
        start = PredictionEmbed.ITEMS_PER_PAGE * self.current_page

        embed = PredictionEmbed(
            guild_name=self.guild_name,
            predictions=self.predictions,
            user_bets=self.user_bets,
            start_offset=start,
        )
        try:
            await self.message.edit(embed=embed, view=self)
        except discord.NotFound:
            self.controller.detach_view(self)

    async def set_selected(self, interaction: discord.Interaction, prediction_id: int):
        await interaction.response.defer()
        self.selected = prediction_id

    async def on_timeout(self):
        with contextlib.suppress(discord.HTTPException):
            await self.message.edit(view=None)
        self.controller.detach_view(self)


class BalanceButton(discord.ui.Button):

    def __init__(self, balance: int):
        self.balance = balance
        super().__init__(label=f"🅱️{balance}", style=discord.ButtonStyle.blurple, row=2)

    async def callback(self, interaction: discord.Interaction):
        view: PredictionView = self.view

        if await view.interaction_check(interaction):
            await interaction.response.defer(ephemeral=True)
            event = UIEvent(UIEventType.SHOW_INVENTORY, interaction)
            await view.controller.dispatch_ui_event(event)


class SelectButton(discord.ui.Button):

    def __init__(self, disabled: bool = False):
        super().__init__(
            label="Place a Bet",
            style=discord.ButtonStyle.green,
            row=2,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: PredictionView = self.view

        if await view.interaction_check(interaction):
            await view.select(interaction)


class PageButton(discord.ui.Button):

    def __init__(self, label: str, right: bool, disabled: bool = False):
        self.right = right
        super().__init__(
            label=label, style=discord.ButtonStyle.grey, row=2, disabled=disabled
        )

    async def callback(self, interaction: discord.Interaction):
        view: PredictionView = self.view

        if await view.interaction_check(interaction):
            await view.flip_page(interaction, self.right)


class CurrentPageButton(discord.ui.Button):

    def __init__(self, label: str):
        super().__init__(
            label=label, style=discord.ButtonStyle.grey, row=2, disabled=True
        )


class SelectDropdown(discord.ui.Select):

    def __init__(
        self, items: list[PredictionStats], selected: int, disabled: bool = False
    ):

        options = []

        for item in items:
            label = (
                (item.prediction.content[:96] + "..")
                if len(item.prediction.content) > 96
                else item.prediction.content
            )

            option = discord.SelectOption(
                label=label,
                description="",
                value=item.prediction.id,
                default=(item.prediction.id == selected),
            )

            options.append(option)

        super().__init__(
            placeholder="Select a Prediction",
            min_values=1,
            max_values=1,
            options=options,
            row=1,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: PredictionView = self.view

        if await view.interaction_check(interaction):
            await view.set_selected(interaction, int(self.values[0]))
