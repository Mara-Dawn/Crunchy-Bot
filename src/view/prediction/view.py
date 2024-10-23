import contextlib

import discord
from control.controller import Controller
from control.types import ControllerType
from datalayer.prediction_stats import PredictionStats
from datalayer.types import PredictionState, PredictionStateSort
from events.types import UIEventType
from events.ui_event import UIEvent
from view.prediction.moderation_embed import PredictionModerationEmbed
from view.view_menu import ViewMenu


class PredictionView(ViewMenu):

    def __init__(
        self,
        controller: Controller,
        interaction: discord.Interaction,
        predictions: list[PredictionStats],
        selected: int = None,
    ):
        super().__init__(timeout=300)
        self.controller = controller
        self.guild_name = interaction.guild.name
        self.member_id = interaction.user.id
        self.guild_id = interaction.guild_id
        self.current_page = 0

        self.filter: list[PredictionState] = [PredictionState.APPROVED]
        self.all_predictions = predictions
        self.predictions: list[PredictionState] = []
        self.__filter_predictions()
        self.__sort_predictions()

        self.selected: int = selected
        self.selected_idx = 0
        if len(self.predictions) > 0 and self.selected is None:
            self.selected = self.predictions[self.selected_idx].prediction.id

        self.user_balance: int = 0
        self.user_bets: dict[int, tuple[int, int]] = {}
        self.selected_outcome: int = None

        self.item_count = len(self.predictions)

        self.message = None

        self.controller_types = [ControllerType.PREDICTION_VIEW]
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
                await self.refresh_ui(user_bets=user_bets, user_balance=user_balance)
            case UIEventType.PREDICTION_REFRESH_ALL:
                predictions = event.payload
                await self.refresh_ui(predictions=predictions)

        if event.view_id != self.id:
            return

        match event.type:
            case UIEventType.PREDICTION_REFRESH:
                predictions = event.payload
                await self.refresh_ui(predictions=predictions)
            case UIEventType.PREDICTION_FULL_REFRESH:
                user_bets = event.payload[1]
                user_balance = event.payload[2]
                await self.refresh_ui(user_bets=user_bets, user_balance=user_balance)

    def __get_selected_prediction_stats(self):
        selected_stats = [
            (idx, prediction)
            for idx, prediction in enumerate(self.predictions)
            if prediction.prediction.id == self.selected
        ]
        if len(selected_stats) > 0:
            return selected_stats[0][0], selected_stats[0][1]
        return 0, None

    def __sort_predictions(self):
        self.predictions = sorted(
            self.predictions,
            key=lambda x: (
                PredictionStateSort.get_prio(x.prediction.state),
                x.prediction.get_timestamp_sort(),
                -x.prediction.id,
            ),
        )

    def __filter_predictions(self):
        self.predictions = [
            prediction
            for prediction in self.all_predictions
            if prediction.prediction.state
            in [PredictionState.APPROVED, PredictionState.LOCKED]
        ]
        self.item_count = len(self.predictions)
        self.page_count = int(
            self.item_count / PredictionModerationEmbed.ITEMS_PER_PAGE
        ) + (self.item_count % PredictionModerationEmbed.ITEMS_PER_PAGE > 0)

    def set_message(self, message: discord.Message):
        self.message = message

    async def submit_bet(
        self, interaction: discord.Interaction, selected_bet_amount: int
    ):
        _, prediction_stats = self.__get_selected_prediction_stats()

        event = UIEvent(
            UIEventType.PREDICTION_PLACE_BET,
            (
                interaction,
                prediction_stats.prediction,
                self.selected_outcome,
                selected_bet_amount,
            ),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def flip_page(self, interaction: discord.Interaction, right: bool = False):
        await interaction.response.defer()
        self.selected_outcome = None
        if len(self.predictions) > 0:
            self.selected_idx = (self.selected_idx + (1 if right else -1)) % len(
                self.predictions
            )
            self.selected = self.predictions[self.selected_idx].prediction.id
        else:
            self.selected_idx = 0

        event = UIEvent(
            UIEventType.PREDICTION_CHANGED,
            self.guild_id,
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    def refresh_elements(
        self,
        user_balance: int = None,
    ):
        page_display = f"Prediction {self.selected_idx + 1}/{len(self.predictions)}"

        if user_balance is not None:
            self.user_balance = user_balance

        _, selected_prediction_stats = self.__get_selected_prediction_stats()

        self.clear_items()

        if selected_prediction_stats is not None:

            disabled = False
            if self.selected in self.user_bets:
                disabled = True
                self.selected_outcome = self.user_bets[self.selected][0]

            outcome_select = OutcomeSelect(
                selected_prediction_stats.prediction.outcomes, disabled=disabled
            )
            for option in outcome_select.options:
                if int(option.value) == self.selected_outcome:
                    option.default = True

            self.add_item(outcome_select)

        bet_label = "Place your Bet"
        if self.selected in self.user_bets:
            bet_label = "Bet More"

        self.add_item(PageButton("<", False))
        self.add_item(BetInputButton(bet_label))
        self.add_item(PageButton(">", True))
        self.add_item(CurrentPageButton(page_display))
        self.add_item(BalanceButton(self.user_balance))

    async def refresh_ui(
        self,
        user_balance: int = None,
        user_bets: dict[int, tuple[int, int]] = None,
        predictions: list[PredictionStats] = None,
    ):

        if user_bets is not None:
            self.user_bets = user_bets

        if predictions is not None:
            self.all_predictions = predictions

        self.__filter_predictions()
        self.__sort_predictions()

        idx, selected_stats = self.__get_selected_prediction_stats()

        selected: PredictionStats = None
        if selected_stats is not None:
            self.selected_idx = idx
            selected = selected_stats

        self.refresh_elements(user_balance)
        embed = None
        user_bet = None
        if selected is not None:
            if self.user_bets is not None and selected.prediction.id in self.user_bets:
                user_bet = self.user_bets[selected.prediction.id]
            embed = selected.get_embed(user_bet)

        try:
            await self.message.edit(embed=embed, view=self)
        except (discord.NotFound, discord.HTTPException):
            self.controller.detach_view(self)

    async def set_outcome(self, outcome_id: int):
        self.selected_outcome = outcome_id
        await self.refresh_ui()

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
            event = UIEvent(UIEventType.SHOW_INVENTORY, interaction, view.id)
            await view.controller.dispatch_ui_event(event)


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


class OutcomeSelect(discord.ui.Select):

    def __init__(self, outcomes: dict[int, str], disabled: bool = False):
        options = []

        outcome_prefixes = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]
        outcome_nr = 0

        for id, text in outcomes.items():
            options.append(
                discord.SelectOption(
                    label=text, value=id, emoji=outcome_prefixes[outcome_nr]
                )
            )
            outcome_nr += 1  # noqa: SIM113

        super().__init__(
            placeholder="Choose an outcome.",
            min_values=1,
            max_values=1,
            options=options,
            disabled=disabled,
            row=0,
        )

    async def callback(self, interaction: discord.Interaction):
        view: PredictionView = self.view
        await interaction.response.defer()
        if await view.interaction_check(interaction):
            await view.set_outcome(int(self.values[0]))


class BetInputButton(discord.ui.Button):

    def __init__(self, label: str = "Place your Bet"):
        super().__init__(label=label, style=discord.ButtonStyle.green, row=2)

    async def callback(self, interaction: discord.Interaction):
        view: PredictionView = self.view
        if await view.interaction_check(interaction):
            await interaction.response.send_modal(BetInputModal(self.view))


class BetInputModal(discord.ui.Modal):

    def __init__(self, view: PredictionView):
        super().__init__(title="Place your Bet")
        self.view = view

        self.amount = discord.ui.TextInput(
            label="Beans",
            placeholder="Enter how many beans you want to bet.",
        )
        self.add_item(self.amount)

    # pylint: disable-next=arguments-differ
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        bet_amount = self.amount.value
        error = False
        try:
            bet_amount = int(bet_amount)
            error = bet_amount < 0
        except ValueError:
            error = True

        if error:
            await interaction.followup.send(
                "Please enter a valid amount of beans above 0.", ephemeral=True
            )
            return

        await self.view.submit_bet(interaction, bet_amount)
