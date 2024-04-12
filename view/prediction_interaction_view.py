import contextlib

import discord

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
        prediction: PredictionStats,
        parent_id: int,
        moderator: bool = False,
    ):
        super().__init__(timeout=200)

        self.controller = controller
        self.parent_id = parent_id
        self.prediction = prediction

        self.message = None
        self.is_moderator = moderator
        self.member_id = interaction.user.id
        self.guild_id = interaction.guild_id

        self.selected_outcome: int = None
        self.selected_bet_amount: int = None

        self.confirm_button: ConfirmButton = None
        self.select_win_button: SelectWinnerButton = None
        self.cancel_button: CancelModerationButton = None
        self.deny_button: DenyButton = None
        self.refund_button: RefundButton = None
        self.approve_button: ApproveButton = None
        self.lock_button: LockButton = None
        self.unlock_button: UnlockButton = None
        self.outcome_select: OutcomeSelect = None
        self.bet_input_button: BetInputButton = None
        self.edit_button: EditButton = None

        self.controller_type = ControllerType.PREDICTION_INTERACTION_VIEW
        self.controller.register_view(self)

        if self.is_moderator:
            match prediction.prediction.state:
                case PredictionState.SUBMITTED:
                    self.deny_button = DenyButton()
                    self.approve_button = ApproveButton()
                    self.edit_button = EditButton(prediction.prediction)
                case PredictionState.APPROVED:
                    self.outcome_select = OutcomeSelect(prediction.prediction.outcomes)
                    self.lock_button = LockButton()
                    self.select_win_button = SelectWinnerButton()
                    self.refund_button = RefundButton()
                    if interaction.user.id == 90043934247501824:
                        self.edit_button = EditButton(prediction.prediction)
                case PredictionState.LOCKED:
                    self.outcome_select = OutcomeSelect(prediction.prediction.outcomes)
                    self.unlock_button = UnlockButton()
                    self.select_win_button = SelectWinnerButton()
                    self.refund_button = RefundButton()
                    self.edit_button = EditButton(prediction.prediction)
                    if interaction.user.id == 90043934247501824:
                        self.edit_button = EditButton(prediction.prediction)
                case PredictionState.DENIED:
                    self.edit_button = EditButton(prediction.prediction)
                    self.approve_button = ApproveButton()

            self.cancel_button: CancelModerationButton = CancelModerationButton()
        elif prediction.prediction.state == PredictionState.APPROVED:
            self.outcome_select = OutcomeSelect(prediction.prediction.outcomes)
            self.bet_input_button = BetInputButton()
            self.confirm_button = ConfirmButton()
            self.cancel_button: CancelButton = CancelButton()

        self.refresh_elements()

    async def listen_for_ui_event(self, event: UIEvent):
        if event.view_id != self.id:
            return

        match event.type:
            case UIEventType.PREDICTION_INTERACTION_REFRESH:
                await self.refresh_ui()
            case UIEventType.PREDICTION_INTERACTION_DISABLE:
                await self.refresh_ui(disabled=event.payload)

    async def submit_bet(self, interaction: discord.Interaction):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.PREDICTION_INTERACTION_PLACE_BET,
            (
                interaction,
                self.prediction.prediction,
                self.selected_outcome,
                self.selected_bet_amount,
            ),
            self.parent_id,
        )
        await self.controller.dispatch_ui_event(event)

    async def confirm_outcome(self, interaction: discord.Interaction):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.PREDICTION_INTERACTION_CONFIRM_OUTCOME,
            (interaction, self.prediction.prediction, self.selected_outcome),
            self.parent_id,
        )
        await self.controller.dispatch_ui_event(event)

    async def deny_submission(self, interaction: discord.Interaction):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.PREDICTION_INTERACTION_DENY,
            (interaction, self.prediction.prediction),
            self.parent_id,
        )
        await self.controller.dispatch_ui_event(event)

    async def end_and_refund_submission(self, interaction: discord.Interaction):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.PREDICTION_INTERACTION_REFUND,
            (interaction, self.prediction.prediction),
            self.parent_id,
        )
        await self.controller.dispatch_ui_event(event)

    async def approve_submission(self, interaction: discord.Interaction):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.PREDICTION_INTERACTION_APPROVE,
            (interaction, self.prediction.prediction),
            self.parent_id,
        )
        await self.controller.dispatch_ui_event(event)

    async def unlock(self, interaction: discord.Interaction):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.PREDICTION_INTERACTION_UNLOCK,
            (interaction, self.prediction.prediction),
            self.parent_id,
        )
        await self.controller.dispatch_ui_event(event)

    async def lock_in(self, interaction: discord.Interaction):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.PREDICTION_INTERACTION_LOCK,
            (interaction, self.prediction.prediction),
            self.parent_id,
        )
        await self.controller.dispatch_ui_event(event)

    async def on_cancel(self, interaction: discord.Interaction):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.PREDICTION_INTERACTION_CANCEL,
            (interaction),
            self.parent_id,
        )
        await self.controller.dispatch_ui_event(event)

    def refresh_elements(self, disabled: bool = False):
        elements: list[discord.ui.Item] = [
            self.outcome_select,
            self.bet_input_button,
            self.confirm_button,
            self.lock_button,
            self.unlock_button,
            self.select_win_button,
            self.approve_button,
            self.edit_button,
            self.deny_button,
            self.refund_button,
            self.cancel_button,
        ]

        if self.bet_input_button is not None:
            if not self.is_moderator and self.selected_bet_amount is not None:
                self.bet_input_button.label = f"Your bet: 🅱️{self.selected_bet_amount}"
            else:
                self.bet_input_button.label = "Enter your Bet"

        self.clear_items()
        for element in elements:
            if element is not None:
                element.disabled = disabled
                self.add_item(element)

    async def refresh_ui(self, disabled: bool = False):
        if self.outcome_select is not None:
            for option in self.outcome_select.options:
                if int(option.value) == self.selected_outcome:
                    option.default = True

        self.refresh_elements(disabled)

        try:
            await self.message.edit(view=self)
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

    async def edit_prediction(
        self, interaction: discord.Interaction, new_prediction: Prediction
    ):
        event = UIEvent(
            UIEventType.PREDICTION_INTERACTION_EDIT,
            (interaction, new_prediction),
            self.parent_id,
        )
        await self.controller.dispatch_ui_event(event)

    async def set_bet_amount(self, bet_amount: int):
        self.selected_bet_amount = bet_amount
        await self.refresh_ui()

    async def set_message(self, message: discord.Message):
        self.message = message

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
        super().__init__(label="Cancel", style=discord.ButtonStyle.red, row=2)

    async def callback(self, interaction: discord.Interaction):
        view: PredictionInteractionView = self.view

        if await view.interaction_check(interaction):
            await view.on_timeout()


class CancelButton(discord.ui.Button):

    def __init__(self):
        super().__init__(label="Cancel", style=discord.ButtonStyle.red, row=2)

    async def callback(self, interaction: discord.Interaction):
        view: PredictionInteractionView = self.view

        if await view.interaction_check(interaction):
            await view.on_cancel(interaction)


class LockButton(discord.ui.Button):

    def __init__(self, label: str = "Lock"):
        super().__init__(label=label, style=discord.ButtonStyle.blurple, row=2)

    async def callback(self, interaction: discord.Interaction):
        view: PredictionInteractionView = self.view

        if await view.interaction_check(interaction):
            await view.lock_in(interaction)


class UnlockButton(discord.ui.Button):

    def __init__(self, label: str = "Unlock"):
        super().__init__(label=label, style=discord.ButtonStyle.blurple, row=2)

    async def callback(self, interaction: discord.Interaction):
        view: PredictionInteractionView = self.view

        if await view.interaction_check(interaction):
            await view.unlock(interaction)


class ConfirmButton(discord.ui.Button):

    def __init__(self, label: str = "Submit"):
        super().__init__(label=label, style=discord.ButtonStyle.green, row=2)

    async def callback(self, interaction: discord.Interaction):
        view: PredictionInteractionView = self.view

        if await view.interaction_check(interaction):
            await view.submit_bet(interaction)


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

        new_prediction = Prediction(
            self.old_prediction.guild_id,
            self.old_prediction.author_id,
            prediction_content,
            outcomes,
            self.old_prediction.state,
            id=self.old_prediction.id,
        )

        await self.view.edit_prediction(interaction, new_prediction)


class BetInputButton(discord.ui.Button):

    def __init__(self):
        super().__init__(label="Enter your Bet", style=discord.ButtonStyle.green, row=2)

    async def callback(self, interaction: discord.Interaction):
        view: PredictionInteractionView = self.view
        if await view.interaction_check(interaction):
            await interaction.response.send_modal(BetInputModal(self.view))


class BetInputModal(discord.ui.Modal):

    def __init__(self, view: PredictionInteractionView):
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

        await self.view.set_bet_amount(bet_amount)
