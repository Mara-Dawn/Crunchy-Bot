import contextlib
import datetime
import os

import discord

from bot import CrunchyBot
from control.controller import Controller
from control.types import ControllerType
from datalayer.prediction import Prediction
from datalayer.prediction_stats import PredictionStats
from datalayer.types import PredictionState
from events.types import UIEventType
from events.ui_event import UIEvent
from view.view_menu import ViewMenu


class PredictionInteractionView(ViewMenu):

    def __init__(
        self,
        controller: Controller,
        interaction: discord.Interaction,
        prediction_stats: PredictionStats,
        parent_id: int,
        moderator: bool = False,
    ):
        super().__init__(timeout=200)

        self.controller = controller
        self.parent_id = parent_id
        self.prediction_stats = prediction_stats

        self.is_moderator = moderator
        self.member_id = interaction.user.id
        self.guild_id = interaction.guild_id

        self.selected_outcome: int = None

        self.controller_types = [ControllerType.PREDICTION_INTERACTION_VIEW]
        self.controller.register_view(self)

        self.select_win_button: SelectWinnerButton = None
        self.cancel_button: CancelModerationButton = None
        self.deny_button: DenyButton = None
        self.refund_button: RefundButton = None
        self.approve_button: ApproveButton = None
        self.lock_button: LockButton = None
        self.unlock_button: UnlockButton = None
        self.outcome_select: OutcomeSelect = None
        self.edit_button: EditButton = None
        self.resubmit_button: ResubmitButton = None
        self.add_timestamp_button: AddLockTimestampButton = None
        self.add_comment_button: AddCommentButton = None

        self.refresh_elements()

    async def listen_for_ui_event(self, event: UIEvent):
        match event.type:
            case UIEventType.PREDICTION_INTERACTION_REFRESH:
                prediction_stats: PredictionStats = event.payload

                if (
                    self.prediction_stats.prediction.id
                    == prediction_stats.prediction.id
                ):
                    self.prediction_stats = prediction_stats

                await self.refresh_ui()

    async def confirm_outcome(self, interaction: discord.Interaction):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.PREDICTION_INTERACTION_CONFIRM_OUTCOME,
            (interaction, self.prediction_stats.prediction, self.selected_outcome),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def deny_submission(self, interaction: discord.Interaction):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.PREDICTION_INTERACTION_DENY,
            (interaction, self.prediction_stats.prediction),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def end_and_refund_submission(self, interaction: discord.Interaction):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.PREDICTION_INTERACTION_REFUND,
            (interaction, self.prediction_stats.prediction),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def approve_submission(self, interaction: discord.Interaction):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.PREDICTION_INTERACTION_APPROVE,
            (interaction, self.prediction_stats.prediction),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def unlock(self, interaction: discord.Interaction):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.PREDICTION_INTERACTION_UNLOCK,
            (interaction, self.prediction_stats.prediction),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def lock_in(self, interaction: discord.Interaction):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.PREDICTION_INTERACTION_LOCK,
            (interaction, self.prediction_stats.prediction),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def resubmit(self, interaction: discord.Interaction):
        await interaction.response.defer()

        old_prediction = self.prediction_stats.prediction

        prediction_object = Prediction(
            interaction.guild_id,
            interaction.user.id,
            old_prediction.content,
            old_prediction.outcomes,
            PredictionState.SUBMITTED,
            moderator_id=None,
            lock_datetime=None,
            comment=old_prediction.comment,
        )

        event = UIEvent(
            UIEventType.PREDICTION_INTERACTION_RESUBMIT,
            (interaction, prediction_object),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def edit_prediction(
        self, interaction: discord.Interaction, new_prediction: Prediction
    ):
        event = UIEvent(
            UIEventType.PREDICTION_INTERACTION_EDIT,
            (interaction, new_prediction),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    def refresh_elements(self, disabled: bool = False):

        self.select_win_button = None
        self.cancel_button = None
        self.deny_button = None
        self.refund_button = None
        self.approve_button = None
        self.lock_button = None
        self.unlock_button = None
        self.outcome_select = None
        self.edit_button = None
        self.resubmit_button = None
        self.add_timestamp_button = None
        self.add_comment_button = None

        match self.prediction_stats.prediction.state:
            case PredictionState.SUBMITTED:
                self.deny_button = DenyButton()
                self.approve_button = ApproveButton()
                self.edit_button = EditButton(self.prediction_stats.prediction)
                self.add_timestamp_button = AddLockTimestampButton(
                    self.prediction_stats.prediction
                )
                self.add_comment_button = AddCommentButton(
                    self.prediction_stats.prediction
                )
            case PredictionState.APPROVED:
                self.outcome_select = OutcomeSelect(
                    self.prediction_stats.prediction.outcomes
                )
                self.lock_button = LockButton()
                self.select_win_button = SelectWinnerButton()
                self.refund_button = RefundButton()
                self.add_timestamp_button = AddLockTimestampButton(
                    self.prediction_stats.prediction
                )
                self.add_comment_button = AddCommentButton(
                    self.prediction_stats.prediction
                )
                if self.member_id == int(os.environ.get(CrunchyBot.ADMIN_ID)):
                    self.edit_button = EditButton(self.prediction_stats.prediction)
            case PredictionState.LOCKED:
                self.outcome_select = OutcomeSelect(
                    self.prediction_stats.prediction.outcomes
                )
                self.unlock_button = UnlockButton()
                self.select_win_button = SelectWinnerButton()
                self.refund_button = RefundButton()
                self.edit_button = EditButton(self.prediction_stats.prediction)
                self.add_comment_button = AddCommentButton(
                    self.prediction_stats.prediction
                )
                if self.member_id == int(os.environ.get(CrunchyBot.ADMIN_ID)):
                    self.edit_button = EditButton(self.prediction_stats.prediction)
            case PredictionState.DENIED:
                self.edit_button = EditButton(self.prediction_stats.prediction)
                self.approve_button = ApproveButton()
                self.add_comment_button = AddCommentButton(
                    self.prediction_stats.prediction
                )
            case PredictionState.DONE | PredictionState.REFUNDED:
                self.resubmit_button = ResubmitButton()

        self.cancel_button: CancelModerationButton = CancelModerationButton()

        if self.outcome_select is not None:
            for option in self.outcome_select.options:
                if int(option.value) == self.selected_outcome:
                    option.default = True

        elements: list[discord.ui.Item] = [
            self.outcome_select,
            self.lock_button,
            self.unlock_button,
            self.select_win_button,
            self.approve_button,
            self.edit_button,
            self.deny_button,
            self.refund_button,
            self.resubmit_button,
            self.add_timestamp_button,
            self.add_comment_button,
            self.cancel_button,
        ]

        self.clear_items()
        for element in elements:
            if element is not None:
                element.disabled = disabled
                self.add_item(element)

    async def refresh_ui(self, disabled: bool = False):
        self.refresh_elements(disabled)

        embed = self.prediction_stats.get_embed(moderator=True)

        try:
            await self.message.edit(embed=embed, view=self)
        except (discord.NotFound, discord.HTTPException):
            self.controller.detach_view(self)

    async def set_outcome(self, outcome_id: int):
        self.selected_outcome = outcome_id
        await self.refresh_ui()

    async def submit_prediction(self, prediction: str, outcomes: list[str]):
        prediction_object = Prediction(
            self.guild_id,
            self.member_id,
            prediction,
            outcomes,
            PredictionState.SUBMITTED,
        )

        event = UIEvent(UIEventType.SHOP_RESPONSE_PREDICTION_SUBMIT, prediction_object)
        await self.controller.dispatch_ui_event(event)
        await self.on_timeout()

    async def on_timeout(self):
        with contextlib.suppress(discord.NotFound):
            await self.message.delete()

        event = UIEvent(
            UIEventType.PREDICTION_INTERACTION_PARENT_CHANGED,
            self.guild_id,
            self.parent_id,
        )
        await self.controller.dispatch_ui_event(event)
        self.controller.detach_view(self)


class CancelModerationButton(discord.ui.Button):

    def __init__(self):
        super().__init__(label="Back", style=discord.ButtonStyle.grey, row=2)

    async def callback(self, interaction: discord.Interaction):
        view: PredictionInteractionView = self.view

        if await view.interaction_check(interaction):
            await view.on_timeout()


class LockButton(discord.ui.Button):

    def __init__(self, label: str = "Lock"):
        super().__init__(label=label, style=discord.ButtonStyle.blurple, row=3)

    async def callback(self, interaction: discord.Interaction):
        view: PredictionInteractionView = self.view

        if await view.interaction_check(interaction):
            await view.lock_in(interaction)


class UnlockButton(discord.ui.Button):

    def __init__(self, label: str = "Unlock"):
        super().__init__(label=label, style=discord.ButtonStyle.blurple, row=3)

    async def callback(self, interaction: discord.Interaction):
        view: PredictionInteractionView = self.view

        if await view.interaction_check(interaction):
            await view.unlock(interaction)


class SelectWinnerButton(discord.ui.Button):

    def __init__(self, label: str = "Confirm Winning Outcome"):
        super().__init__(label=label, style=discord.ButtonStyle.green, row=2)

    async def callback(self, interaction: discord.Interaction):
        view: PredictionInteractionView = self.view

        if await view.interaction_check(interaction):
            await view.confirm_outcome(interaction)


class DenyButton(discord.ui.Button):

    def __init__(self, label: str = "Deny"):
        super().__init__(label=label, style=discord.ButtonStyle.red, row=2)

    async def callback(self, interaction: discord.Interaction):
        view: PredictionInteractionView = self.view

        if await view.interaction_check(interaction):
            await view.deny_submission(interaction)


class ApproveButton(discord.ui.Button):

    def __init__(self, label: str = "Approve"):
        super().__init__(label=label, style=discord.ButtonStyle.green, row=2)

    async def callback(self, interaction: discord.Interaction):
        view: PredictionInteractionView = self.view

        if await view.interaction_check(interaction):
            await view.approve_submission(interaction)


class ResubmitButton(discord.ui.Button):

    def __init__(self, label: str = "Resubmit"):
        super().__init__(label=label, style=discord.ButtonStyle.green, row=2)

    async def callback(self, interaction: discord.Interaction):
        view: PredictionInteractionView = self.view

        if await view.interaction_check(interaction):
            await view.resubmit(interaction)


class RefundButton(discord.ui.Button):

    def __init__(self, label: str = "End and Refund"):
        super().__init__(label=label, style=discord.ButtonStyle.red, row=2)

    async def callback(self, interaction: discord.Interaction):
        view: PredictionInteractionView = self.view

        if await view.interaction_check(interaction):
            await view.end_and_refund_submission(interaction)


class OutcomeSelect(discord.ui.Select):

    def __init__(self, outcomes: dict[int, str]):
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
            row=0,
        )

    async def callback(self, interaction: discord.Interaction):
        view: PredictionInteractionView = self.view
        await interaction.response.defer()
        if await view.interaction_check(interaction):
            await view.set_outcome(int(self.values[0]))


class AddLockTimestampButton(discord.ui.Button):
    def __init__(self, prediction: Prediction):
        super().__init__(
            label="Set Lock Timestamp", style=discord.ButtonStyle.blurple, row=3
        )
        self.prediction = prediction

    async def callback(self, interaction: discord.Interaction):
        view: PredictionInteractionView = self.view
        if await view.interaction_check(interaction):
            await interaction.response.send_modal(
                AddLockTimestampModal(self.view, self.prediction)
            )


class AddLockTimestampModal(discord.ui.Modal):

    def __init__(self, view: PredictionInteractionView, prediction: Prediction):
        title = "Set Lock Timestamp"
        super().__init__(title=title)

        self.format = "%d/%m/%Y %H:%M"
        self.view = view
        self.old_prediction = prediction

        self.timestamp = discord.ui.TextInput(
            label="Timestamp (UTC - 24h format):",
            placeholder="DD/MM/YYYY HH:MM",
        )

        old_timestamp = prediction.lock_datetime
        if old_timestamp is not None:
            self.timestamp.default = old_timestamp.strftime(self.format)
        else:
            self.timestamp.default = datetime.datetime.now().strftime(self.format)

        self.add_item(self.timestamp)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()

        try:
            timestamp = datetime.datetime.strptime(self.timestamp.value, self.format)
        except ValueError:
            await interaction.followup.send(
                "Please enter a valid timestamp.", ephemeral=True
            )
            return

        prediction = self.old_prediction
        prediction.lock_datetime = timestamp

        await self.view.edit_prediction(interaction, prediction)


class AddCommentButton(discord.ui.Button):
    def __init__(self, prediction: Prediction):
        super().__init__(label="Add Comment", style=discord.ButtonStyle.grey, row=3)
        self.prediction = prediction

    async def callback(self, interaction: discord.Interaction):
        view: PredictionInteractionView = self.view
        if await view.interaction_check(interaction):
            await interaction.response.send_modal(
                AddCommentModal(self.view, self.prediction)
            )


class AddCommentModal(discord.ui.Modal):

    def __init__(self, view: PredictionInteractionView, prediction: Prediction):
        title = "Add or Edit Comment"
        super().__init__(title=title)

        self.view = view
        self.old_prediction = prediction

        self.comment = discord.ui.TextInput(
            label="Comment:",
            placeholder="Add a comment here.",
        )

        old_comment = prediction.comment
        if old_comment is not None:
            self.comment.default = old_comment

        self.add_item(self.comment)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        prediction = self.old_prediction
        prediction.comment = self.comment.value
        await self.view.edit_prediction(interaction, prediction)


class EditButton(discord.ui.Button):
    def __init__(self, prediction: Prediction = None):
        super().__init__(label="Edit", style=discord.ButtonStyle.grey, row=2)
        self.prediction = prediction

    async def callback(self, interaction: discord.Interaction):
        view: PredictionInteractionView = self.view
        if await view.interaction_check(interaction):
            await interaction.response.send_modal(EditModal(self.view, self.prediction))


class EditModal(discord.ui.Modal):

    def __init__(self, view: PredictionInteractionView, prediction: Prediction = None):
        title = "Edit Prediction"
        if prediction is None:
            title = "Submit Prediction"
        super().__init__(title=title)

        self.view = view
        self.old_prediction = prediction

        self.prediction = discord.ui.TextInput(
            label="Prediction:",
            placeholder="Enter your Prediction here.",
        )
        if prediction is not None:
            self.prediction.default = prediction.content

        self.add_item(self.prediction)
        self.outcomes: list[discord.ui.TextInput] = []

        for i in range(4):
            required = True
            if i >= 2:
                required = False

            default = None
            custom_id = i
            if prediction is not None:
                if len(prediction.outcomes) > i:
                    custom_id = list(prediction.outcomes)[i]
                    default = list(prediction.outcomes.values())[i]
                else:
                    continue

            outcome = discord.ui.TextInput(
                label=f"Outcome {i+1}:",
                required=required,
                custom_id=str(custom_id),
                default=default,
            )
            self.outcomes.append(outcome)
            self.add_item(outcome)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        outcomes = {
            int(outcome.custom_id): outcome.value
            for outcome in self.outcomes
            if len(outcome.value) > 0
        }
        prediction_content = self.prediction.value

        if len(prediction_content) < 5:
            await interaction.followup.send("Prediction too short.", ephemeral=True)
            return

        if self.old_prediction is None:
            await self.view.submit_prediction(prediction_content, outcomes)
            return

        prediction = self.old_prediction
        prediction.content = prediction_content
        prediction.outcomes = outcomes

        await self.view.edit_prediction(interaction, prediction)
