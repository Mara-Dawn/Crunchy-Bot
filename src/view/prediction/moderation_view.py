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


class PredictionModerationView(ViewMenu):

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

        self.filter: list[PredictionState] = [PredictionState.SUBMITTED]
        self.all_predictions = predictions
        self.predictions = []
        self.__sort_predictions()
        self.__filter_predictions()

        self.selected: int = None

        self.item_count = len(self.predictions)
        self.page_count = int(
            self.item_count / PredictionModerationEmbed.ITEMS_PER_PAGE
        ) + (self.item_count % PredictionModerationEmbed.ITEMS_PER_PAGE > 0)

        self.disabled = False

        self.controller_types = [ControllerType.PREDICTION_MODERATION_VIEW]
        self.controller.register_view(self)
        self.refresh_elements()

    async def listen_for_ui_event(self, event: UIEvent):
        match event.type:
            case UIEventType.PREDICTION_MODERATION_REFRESH_ALL:
                predictions = event.payload
                await self.refresh_ui(predictions=predictions)

        if event.view_id != self.id:
            return

        match event.type:
            case UIEventType.PREDICTION_MODERATION_REFRESH:
                predictions = event.payload
                await self.refresh_ui(predictions=predictions)
            case UIEventType.PREDICTION_MODERATION_DISABLE:
                await self.refresh_ui(disabled=event.payload)

    def __sort_predictions(self):
        self.all_predictions = sorted(
            self.all_predictions,
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
            if prediction.prediction.state in self.filter
        ]
        self.item_count = len(self.predictions)
        self.page_count = int(
            self.item_count / PredictionModerationEmbed.ITEMS_PER_PAGE
        ) + (self.item_count % PredictionModerationEmbed.ITEMS_PER_PAGE > 0)

    async def edit(self, interaction: discord.Interaction):
        await interaction.response.defer()

        selected_stats = [
            prediction
            for prediction in self.predictions
            if prediction.prediction.id == self.selected
        ]

        selected = None
        if len(selected_stats) > 0:
            selected = selected_stats[0]

        event = UIEvent(
            UIEventType.PREDICTION_MODERATION_EDIT,
            (interaction, selected),
            self.id,
        )
        self.selected = None
        await self.controller.dispatch_ui_event(event)

    async def flip_page(self, interaction: discord.Interaction, right: bool = False):
        await interaction.response.defer()
        if self.page_count > 0:
            self.current_page = (
                self.current_page + (1 if right else -1)
            ) % self.page_count
        self.selected = None
        event = UIEvent(
            UIEventType.PREDICTION_MODERATION_CHANGED,
            self.guild_id,
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    def refresh_elements(self, disabled: bool = False):
        start = PredictionModerationEmbed.ITEMS_PER_PAGE * self.current_page
        end = min((start + PredictionModerationEmbed.ITEMS_PER_PAGE), self.item_count)
        page_display = f"Page {self.current_page + 1}/{max(1,self.page_count)}"

        self.disabled = disabled

        if len(self.predictions) > 0 and self.selected is None:
            self.selected = self.predictions[start:end][0].prediction.id

        self.clear_items()
        self.add_item(FilterDropdown(self.filter, disabled))
        if len(self.predictions[start:end]) > 0:
            self.add_item(
                SelectDropdown(self.predictions[start:end], self.selected, disabled)
            )
        self.add_item(PageButton("<", False, disabled))
        self.add_item(EditButton(disabled))
        self.add_item(PageButton(">", True, disabled))
        self.add_item(CurrentPageButton(page_display))

    async def refresh_ui(
        self, predictions: list[PredictionStats] = None, disabled: bool = None
    ):
        if disabled is None:
            disabled = self.disabled

        if predictions is not None:
            self.all_predictions = predictions
            self.__sort_predictions()

        self.__filter_predictions()

        self.refresh_elements(disabled)

        author_name = self.controller.bot.user.display_name
        author_img = self.controller.bot.user.display_avatar
        embed = PredictionModerationEmbed(
            author_name, author_img, guild_name=self.guild_name
        )

        embeds = [embed]

        start = PredictionModerationEmbed.ITEMS_PER_PAGE * self.current_page
        end_offset = min(
            (start + PredictionModerationEmbed.ITEMS_PER_PAGE), len(self.predictions)
        )
        display = self.predictions[start:end_offset]

        for prediction in display:
            embeds.append(prediction.get_embed(moderator=True))

        try:
            await self.message.edit(embeds=embeds, view=self)
        except discord.NotFound:
            self.controller.detach_view(self)

    async def set_filter(
        self, interaction: discord.Interaction, filter: list[PredictionState]
    ):
        await interaction.response.defer()
        self.filter = filter
        self.current_page = 0
        self.selected = None
        await self.refresh_ui()

    async def set_selected(self, interaction: discord.Interaction, prediction_id: int):
        await interaction.response.defer()
        self.selected = prediction_id

    async def on_timeout(self):
        with contextlib.suppress(discord.HTTPException):
            await self.message.edit(view=None)
        self.controller.detach_view(self)


class EditButton(discord.ui.Button):

    def __init__(self, disabled: bool = False):
        super().__init__(
            label="Show Options",
            style=discord.ButtonStyle.green,
            row=2,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: PredictionModerationView = self.view

        if await view.interaction_check(interaction):
            await view.edit(interaction)


class PageButton(discord.ui.Button):

    def __init__(self, label: str, right: bool, disabled: bool = False):
        self.right = right
        super().__init__(
            label=label, style=discord.ButtonStyle.grey, row=2, disabled=disabled
        )

    async def callback(self, interaction: discord.Interaction):
        view: PredictionModerationView = self.view

        if await view.interaction_check(interaction):
            await view.flip_page(interaction, self.right)


class CurrentPageButton(discord.ui.Button):

    def __init__(self, label: str):
        super().__init__(
            label=label, style=discord.ButtonStyle.grey, row=2, disabled=True
        )


class BalanceButton(discord.ui.Button):

    def __init__(self, balance: int):
        self.balance = balance
        super().__init__(label=f"🅱️{balance}", style=discord.ButtonStyle.blurple, row=2)

    async def callback(self, interaction: discord.Interaction):
        view: PredictionModerationView = self.view

        if await view.interaction_check(interaction):
            await interaction.response.defer(ephemeral=True)
            event = UIEvent(UIEventType.SHOW_INVENTORY, interaction, view.id)
            await view.controller.dispatch_ui_event(event)


class FilterDropdown(discord.ui.Select):

    def __init__(
        self,
        selected: list[PredictionState],
        disabled: bool = False,
    ):

        options = []

        for state in PredictionState:

            option = discord.SelectOption(
                label=state.value,
                description="",
                value=state,
                default=(state in selected),
            )

            options.append(option)

        super().__init__(
            placeholder="Filter Predictions",
            min_values=1,
            max_values=len(PredictionState),
            options=options,
            row=0,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: PredictionModerationView = self.view

        if await view.interaction_check(interaction):
            await view.set_filter(interaction, self.values)


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
        view: PredictionModerationView = self.view

        if await view.interaction_check(interaction):
            await view.set_selected(interaction, int(self.values[0]))
