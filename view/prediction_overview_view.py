import contextlib

import discord

from control.controller import Controller
from control.types import ControllerType
from datalayer.prediction_stats import PredictionStats
from events.types import UIEventType
from events.ui_event import UIEvent
from view.view_menu import ViewMenu


class PredictionOverviewView(ViewMenu):

    def __init__(
        self,
        controller: Controller,
        prediction_stats: PredictionStats,
    ):
        super().__init__(timeout=None)
        self.controller = controller

        self.prediction_stats = prediction_stats

        self.controller_type = ControllerType.PREDICTION_VIEW
        self.controller.register_view(self)

        self.refresh_elements()

    async def listen_for_ui_event(self, event: UIEvent):
        match event.type:
            case UIEventType.PREDICTION_OVERVIEW_REFRESH:
                prediction_stats: PredictionStats = event.payload
                if (
                    self.prediction_stats.prediction.id
                    != prediction_stats.prediction.id
                ):
                    return
                await self.refresh_ui(prediction_stats)

    def refresh_elements(self):

        self.clear_items()

        for idx, outcome in enumerate(self.prediction_stats.prediction.outcomes):
            self.add_item(
                BetInputButton(
                    idx, outcome, self.prediction_stats.prediction.outcomes[outcome]
                )
            )

        total = sum(self.prediction_stats.bets.values())
        self.add_item(
            TotalPotButton(
                pot=total,
            )
        )

    async def refresh_ui(
        self,
        prediction_stats: PredictionStats = None,
    ):

        if prediction_stats is not None:
            self.prediction_stats = prediction_stats

        self.refresh_elements()
        embed = self.prediction_stats.get_embed()
        try:
            await self.message.edit(embed=embed, view=self)
        except (discord.NotFound, discord.HTTPException):
            self.controller.detach_view(self)

    async def send_response(self, interaction: discord.Interaction):
        event = UIEvent(
            UIEventType.PREDICTION_OPEN_UI,
            (interaction, self.prediction_stats.prediction),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def submit_bet(
        self,
        interaction: discord.Interaction,
        selected_bet_amount: int,
        outcome_id: int,
    ):
        event = UIEvent(
            UIEventType.PREDICTION_PLACE_BET,
            (
                interaction,
                self.prediction_stats.prediction,
                outcome_id,
                selected_bet_amount,
            ),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return True

    async def on_timeout(self):
        with contextlib.suppress(discord.HTTPException):
            await self.message.edit(view=None)
        self.controller.detach_view(self)


class ParticipateButton(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label="Participate In This Prediction",
            style=discord.ButtonStyle.green,
            row=0,
        )

    async def callback(self, interaction: discord.Interaction):
        view: PredictionOverviewView = self.view
        await view.send_response(interaction)


class InfoButton(discord.ui.Button):

    def __init__(
        self,
    ):
        super().__init__(
            label="Place your bet here:",
            style=discord.ButtonStyle.grey,
            row=0,
        )


class BetInputButton(discord.ui.Button):

    def __init__(self, label: int, outcome_id: int, outcome_text: str):

        outcome_prefixes = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]
        self.outcome_id = outcome_id
        self.outcome_text = outcome_text
        super().__init__(
            label=f"Bet On {outcome_prefixes[label]}",
            style=discord.ButtonStyle.green,
            row=0,
        )

    async def callback(self, interaction: discord.Interaction):
        view: PredictionOverviewView = self.view
        if await view.interaction_check(interaction):
            await interaction.response.send_modal(
                BetInputModal(self.view, self.outcome_id, self.outcome_text)
            )


class BetInputModal(discord.ui.Modal):

    def __init__(
        self, view: PredictionOverviewView, outcome_id: int, outcome_text: str
    ):
        super().__init__(title="Place your Bet")
        self.view = view
        self.outcome_id = outcome_id

        self.amount = discord.ui.TextInput(
            label=f'Beans bet on "{outcome_text[:20]}"',
            placeholder="Enter how many beans you want to bet.",
        )
        self.add_item(self.amount)

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

        await self.view.submit_bet(interaction, bet_amount, self.outcome_id)


class TotalPotButton(discord.ui.Button):

    def __init__(self, pot: int):
        self.pot = pot
        super().__init__(
            label=f"Total Pot: 🅱️{pot}",
            style=discord.ButtonStyle.blurple,
            row=0,
        )

    async def callback(self, interaction: discord.Interaction):
        view: PredictionOverviewView = self.view
        await view.send_response(interaction)
