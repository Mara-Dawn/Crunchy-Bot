import contextlib
import re

import discord

from control.controller import Controller
from control.types import ControllerType
from datalayer.prediction import Prediction
from datalayer.types import PredictionState
from events.types import UIEventType
from events.ui_event import UIEvent
from items.item import Item
from view.types import EmojiType
from view.view_menu import ViewMenu


class ShopResponseView(ViewMenu):

    def __init__(
        self,
        controller: Controller,
        interaction: discord.Interaction,
        item: Item,
        parent_id: int,
    ):
        super().__init__(timeout=200)

        self.controller = controller
        self.parent_id = parent_id
        self.type = None
        if item is not None:
            self.type = item.type
        self.item = item

        self.member_id = interaction.user.id
        self.guild_id = interaction.guild_id

        self.selected_user: discord.Member = None
        self.selected_amount: int = 1
        self.selected_color: str = None
        self.selected_emoji: discord.Emoji | str = None
        self.selected_emoji_type: EmojiType = None

        self.confirm_button: ConfirmButton = None
        self.cancel_button: CancelButton = None
        self.user_select: UserPicker = None
        self.color_input_button: ColorInputButton = None
        self.amount_select: AmountInput = None
        self.reaction_input_button: ReactionInputButton = None
        self.submission_button: SubmissionInputButton = None

        self.controller_types = [ControllerType.SHOP_RESPONSE_VIEW]
        self.controller.register_view(self)

    async def init(self):
        pass

    async def listen_for_ui_event(self, event: UIEvent):
        if event.view_id != self.id:
            return

        match event.type:
            case UIEventType.SHOP_RESPONSE_REFRESH:
                await self.refresh_ui()
            case UIEventType.SHOP_RESPONSE_DISABLE:
                await self.refresh_ui(disabled=event.payload)
            case UIEventType.SHOP_RESPONSE_EMOJI_UPDATE:
                self.selected_emoji = event.payload[0]
                self.selected_emoji_type = event.payload[1]
                await self.refresh_ui()

    async def submit(self, interaction: discord.Interaction):
        pass

    def refresh_elements(self, disabled: bool = False):
        elements: list[discord.ui.Item] = [
            self.user_select,
            self.amount_select,
            self.color_input_button,
            self.reaction_input_button,
            self.submission_button,
            self.confirm_button,
            self.cancel_button,
        ]

        self.clear_items()
        for element in elements:
            if element is self.amount_select and not self.item.allow_amount:
                continue
            if element is not None:
                element.disabled = disabled
                self.add_item(element)

    async def refresh_ui(
        self, disabled: bool = False, force_embed: discord.Embed = None
    ):
        color = discord.Colour.purple()
        if self.selected_color is not None:
            hex_value = int(self.selected_color, 16)
            color = discord.Color(hex_value)

        embed = force_embed
        if embed is None:
            embed = self.item.get_embed(
                self.controller.bot,
                show_price=True,
                color=color,
                count=self.selected_amount,
                show_title=False,
            )

        emoji = self.item.emoji
        if isinstance(self.item.emoji, int):
            emoji = str(self.controller.bot.get_emoji(self.item.emoji))
        embed.title = f"{emoji} {self.item.name} {emoji}"

        if self.selected_amount > 1:
            embed.title = f"{self.selected_amount}x {embed.title}"
        if self.selected_color is not None:
            embed.title = f"{embed.title} [#{self.selected_color}]"
        if self.selected_emoji is not None:
            embed.title = f"{embed.title} - Selected: {str(self.selected_emoji)}"

        embed.title = f"> {embed.title}"

        if self.amount_select is not None:
            self.amount_select.options[self.selected_amount - 1].default = True

        self.refresh_elements(disabled)

        try:
            await self.message.edit(embed=embed, view=self)
        except (discord.NotFound, discord.HTTPException):
            self.controller.detach_view(self)

    async def set_amount(self, amount: int):
        self.amount_select.options[self.selected_amount - 1].default = False
        self.selected_amount = amount
        await self.refresh_ui()

    async def set_selected(self, member: discord.Member):
        self.selected_user = member
        await self.refresh_ui()

    async def set_color(self, color: str):
        self.selected_color = color.lstrip("#")
        await self.refresh_ui()

    async def set_emoji(self, emoji: discord.Emoji | str, emoji_type: EmojiType):
        self.selected_emoji = emoji
        self.selected_emoji_type = emoji_type
        await self.refresh_ui()

    async def submit_prediction(self, prediction: str, outcomes: list[str]):
        prediction_object = Prediction(
            self.guild_id,
            self.member_id,
            prediction,
            outcomes,
            PredictionState.SUBMITTED,
        )

        event = UIEvent(
            UIEventType.SHOP_RESPONSE_PREDICTION_SUBMIT,
            prediction_object,
        )
        await self.controller.dispatch_ui_event(event)
        await self.on_timeout()

    def get_data(self):
        return ShopResponseData(
            item=self.item,
            selected_user=self.selected_user,
            selected_amount=self.selected_amount,
            selected_color=self.selected_color,
            selected_emoji=self.selected_emoji,
            selected_emoji_type=self.selected_emoji_type,
            confirm_button=self.confirm_button,
            cancel_button=self.cancel_button,
            user_select=self.user_select,
            color_input_button=self.color_input_button,
            amount_select=self.amount_select,
            reaction_input_button=self.reaction_input_button,
        )

    async def on_timeout(self):
        with contextlib.suppress(discord.NotFound):
            await self.message.delete()

        event = UIEvent(
            UIEventType.SHOP_CHANGED,
            (self.guild_id, self.member_id),
            self.parent_id,
        )
        await self.controller.dispatch_ui_event(event)
        self.controller.detach_view(self)


class UserPicker(discord.ui.UserSelect):

    def __init__(self):
        super().__init__(
            placeholder="Select a user.", min_values=1, max_values=1, row=0
        )

    async def callback(self, interaction: discord.Interaction):
        view: ShopResponseView = self.view
        await interaction.response.defer()

        if await view.interaction_check(interaction):
            await view.set_selected(self.values[0])


class CancelButton(discord.ui.Button):

    def __init__(self):
        super().__init__(label="Cancel", style=discord.ButtonStyle.red, row=2)

    async def callback(self, interaction: discord.Interaction):
        view: ShopResponseView = self.view

        if await view.interaction_check(interaction):
            await view.on_timeout()


class ConfirmButton(discord.ui.Button):

    def __init__(self, label: str = "Confirm"):
        super().__init__(label=label, style=discord.ButtonStyle.green, row=2)

    async def callback(self, interaction: discord.Interaction):
        view: ShopResponseView = self.view

        if await view.interaction_check(interaction):
            await view.submit(interaction)


class AmountInput(discord.ui.Select):

    def __init__(self, suffix: str = ""):
        options = []

        for i in range(1, 26):
            options.append(
                discord.SelectOption(label=f"{i}{suffix}", value=i, default=(i == 1))
            )

        super().__init__(
            placeholder="Choose the amount.",
            min_values=1,
            max_values=1,
            options=options,
            row=1,
        )

    async def callback(self, interaction: discord.Interaction):
        view: ShopResponseView = self.view
        await interaction.response.defer()
        if await view.interaction_check(interaction):
            await view.set_amount(int(self.values[0]))


class ColorInputButton(discord.ui.Button):

    def __init__(self, default_color: str):
        super().__init__(label="Pick a Color", style=discord.ButtonStyle.green, row=2)
        self.default_color = default_color

    async def callback(self, interaction: discord.Interaction):
        view: ShopResponseView = self.view
        if await view.interaction_check(interaction):
            await interaction.response.send_modal(
                ColorInputModal(self.view, self.default_color)
            )


class ColorInputModal(discord.ui.Modal):

    def __init__(self, view: ShopResponseView, default_color: str):
        super().__init__(title="Choose a Color")
        self.view = view
        if default_color is not None:
            default_color = f"#{default_color}"
        self.hex_color = discord.ui.TextInput(
            label="Hex Color Code", placeholder="#FFFFFF", default=default_color
        )
        self.add_item(self.hex_color)

    # pylint: disable-next=arguments-differ
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        hex_string = self.hex_color.value
        match = re.search(r"^#(?:[0-9a-fA-F]{3}){1,2}$", hex_string)
        if not match:
            await interaction.followup.send(
                "Please enter a valid hex color value.", ephemeral=True
            )
            return

        await self.view.set_color(hex_string)


class ReactionInputButton(discord.ui.Button):

    def __init__(self):
        super().__init__(label="Select Emoji", style=discord.ButtonStyle.green, row=2)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        parent: ShopResponseView = self.view
        if await parent.interaction_check(interaction):
            await parent.refresh_ui(disabled=True)

            content = f"<@{interaction.user.id}> please react to this message with the emoji of your choice."
            view = ReactionInputView(
                parent.controller, interaction, parent.item, parent.id
            )
            message = await interaction.followup.send(content, view=view)
            view.set_message(message)


class ReactionInputView(ShopResponseView):

    def __init__(
        self,
        controller: Controller,
        interaction: discord.Interaction,
        item: Item,
        parent_id: int,
    ):
        super().__init__(controller, interaction, item, parent_id)

        self.confirm_button = ConfirmButton("Confirm")
        self.cancel_button = CancelButton()

        self.refresh_elements()
        self.controller.register_view(self)

    async def listen_for_ui_event(self, event: UIEvent):
        pass

    async def submit(self, interaction: discord.Interaction):
        if await self.interaction_check(interaction):
            event = UIEvent(
                UIEventType.REACTION_SELECTED,
                (interaction, self.message),
                self.parent_id,
            )
            await self.controller.dispatch_ui_event(event)

    async def on_timeout(self):
        with contextlib.suppress(discord.NotFound):
            await self.message.delete()

        event = UIEvent(
            UIEventType.SHOP_RESPONSE_REFRESH,
            None,
            self.parent_id,
        )
        await self.controller.dispatch_ui_event(event)
        self.controller.detach_view(self)


class SubmissionInputButton(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label="Enter your Prediction", style=discord.ButtonStyle.green, row=2
        )

    async def callback(self, interaction: discord.Interaction):
        view: ShopResponseView = self.view
        if await view.interaction_check(interaction):
            await interaction.response.send_modal(SubmissionInputModal(self.view))


class SubmissionInputModal(discord.ui.Modal):

    def __init__(self, view: ShopResponseView):
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

        await self.view.submit_prediction(prediction, outcomes)


class ShopResponseData:
    def __init__(
        self,
        item: Item,
        selected_user: discord.Member,
        selected_amount: int,
        selected_color: str,
        selected_emoji: discord.Emoji | str,
        selected_emoji_type: EmojiType,
        confirm_button: ConfirmButton,
        cancel_button: CancelButton,
        user_select: UserPicker,
        color_input_button: ColorInputButton,
        amount_select: AmountInput,
        reaction_input_button: ReactionInputButton,
    ):
        self.item = item
        self.type = None
        if item is not None:
            self.type = item.type
        self.selected_user = selected_user
        self.selected_amount = selected_amount
        self.selected_color = selected_color
        self.selected_emoji = selected_emoji
        self.selected_emoji_type = selected_emoji_type

        self.confirm_button = confirm_button
        self.cancel_button = cancel_button
        self.user_select = user_select
        self.color_input_button = color_input_button
        self.amount_select = amount_select
        self.reaction_input_button = reaction_input_button
