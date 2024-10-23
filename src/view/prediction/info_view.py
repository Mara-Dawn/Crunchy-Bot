import contextlib

import discord

from control.controller import Controller
from control.types import ControllerType
from datalayer.prediction import Prediction
from datalayer.types import PredictionState
from events.types import UIEventType
from events.ui_event import UIEvent
from view.view_menu import ViewMenu


class PredictionInfoView(ViewMenu):

    def __init__(
        self,
        controller: Controller,
    ):
        super().__init__(timeout=None)
        self.controller = controller

        self.controller_types = [ControllerType.PREDICTION_VIEW]
        self.controller.register_view(self)

        self.reload_elements()

    async def listen_for_ui_event(self, event: UIEvent):
        pass

    def reload_elements(self):
        self.clear_items()
        self.add_item(OverviewButton())
        self.add_item(SubmissionInputButton())

    async def send_response(self, interaction: discord.Interaction):
        event = UIEvent(
            UIEventType.PREDICTION_OPEN_UI,
            (interaction, None),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def submit_prediction(
        self, interaction: discord.Interaction, prediction: str, outcomes: list[str]
    ):
        prediction_object = Prediction(
            interaction.guild_id,
            interaction.user.id,
            prediction,
            outcomes,
            PredictionState.SUBMITTED,
        )

        event = UIEvent(
            UIEventType.PREDICTION_PREDICTION_SUBMIT,
            prediction_object,
        )
        await self.controller.dispatch_ui_event(event)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return True

    async def on_timeout(self):
        with contextlib.suppress(discord.HTTPException):
            await self.message.edit(view=None)
        self.controller.detach_view(self)


class OverviewButton(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label="Manage Your Current Bets",
            style=discord.ButtonStyle.green,
            row=0,
            custom_id="OverviewButton",
        )

    async def callback(self, interaction: discord.Interaction):
        view: PredictionInfoView = self.view
        await view.send_response(interaction)


class SubmissionInputButton(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label="Submit A New Prediction Idea",
            style=discord.ButtonStyle.blurple,
            row=0,
            custom_id="SubmissionInputButton",
        )

    async def callback(self, interaction: discord.Interaction):
        view: PredictionInfoView = self.view
        if await view.interaction_check(interaction):
            await interaction.response.send_modal(SubmissionInputModal(self.view))


class SubmissionInputModal(discord.ui.Modal):

    def __init__(self, view: PredictionInfoView):
        super().__init__(title="Prediction Submission")
        self.view = view
        self.prediction = discord.ui.TextInput(
            label="Prediction:", placeholder="Enter your Prediction here."
        )
        self.add_item(self.prediction)
        self.outcomes: list[discord.ui.TextInput] = []

        for i in range(4):
            required = True
            if i >= 2:
                required = False
            outcome = discord.ui.TextInput(
                label=f"Outcome {i+1}:", required=required, custom_id=str(i)
            )
            self.outcomes.append(outcome)
            self.add_item(outcome)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        prediction = self.prediction.value
        outcomes = {
            int(outcome.custom_id): outcome.value
            for outcome in self.outcomes
            if len(outcome.value) > 0
        }

        if len(prediction) < 5:
            await interaction.followup.send("Prediction too short.", ephemeral=True)
            return

        if len(outcomes) < 2:
            await interaction.followup.send(
                "Please submit at least two possible outcomes.", ephemeral=True
            )
            return

        await interaction.followup.send(
            "Thank you for your submission, it will be reviewed by the mods.",
            ephemeral=True,
        )

        await self.view.submit_prediction(interaction, prediction, outcomes)
