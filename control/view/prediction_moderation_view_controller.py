import discord
from discord.ext import commands

from control.controller import Controller
from control.logger import BotLogger
from control.view.view_controller import ViewController
from datalayer.database import Database
from datalayer.prediction_stats import PredictionStats
from events.bot_event import BotEvent
from events.prediction_event import PredictionEvent
from events.types import EventType, UIEventType
from events.ui_event import UIEvent
from view.prediction_interaction_view import PredictionInteractionView
from view.shop_color_select_view import ShopColorSelectView  # noqa: F401
from view.shop_confirm_view import ShopConfirmView  # noqa: F401
from view.shop_prediction_submission_view import (
    ShopPredictionSubmissionView,  # noqa: F401
)
from view.shop_reaction_select_view import ShopReactionSelectView  # noqa: F401

# noqa: F401
from view.shop_user_select_view import ShopUserSelectView  # noqa: F401


class PredictionModerationViewController(ViewController):

    def __init__(
        self,
        bot: commands.Bot,
        logger: BotLogger,
        database: Database,
        controller: Controller,
    ):
        super().__init__(
            bot,
            logger,
            database,
        )
        self.controller = controller

    async def listen_for_event(self, event: BotEvent) -> None:
        match event.type:
            case EventType.PREDICTION:
                prediction_event: PredictionEvent = event
                prediction_stats = self.database.get_prediction_stats_by_guild(
                    prediction_event.guild_id
                )
                event = UIEvent(
                    UIEventType.PREDICTION_MODERATION_REFRESH_ALL,
                    prediction_stats,
                )
                await self.controller.dispatch_ui_event(event)

    async def listen_for_ui_event(self, event: UIEvent):
        match event.type:
            case UIEventType.PREDICTION_MODERATION_EDIT:
                interaction = event.payload[0]
                selected_prediction = event.payload[1]
                await self.edit(interaction, selected_prediction, event.view_id)
            case (
                UIEventType.PREDICTION_MODERATION_CHANGED
                | UIEventType.PREDICTION_INTERACTION_PARENT_CHANGED
            ):
                guild_id = event.payload
                await self.refresh_ui(guild_id, event.view_id)

    async def refresh_ui(self, guild_id: int, view_id: int):
        prediction_stats = self.database.get_prediction_stats_by_guild(guild_id)
        event = UIEvent(
            UIEventType.PREDICTION_MODERATION_REFRESH, prediction_stats, view_id
        )
        await self.controller.dispatch_ui_event(event)
        event = UIEvent(UIEventType.PREDICTION_MODERATION_DISABLE, False, view_id)
        await self.controller.dispatch_ui_event(event)

    async def edit(
        self, interaction: discord.Interaction, selected: PredictionStats, view_id: int
    ):
        if selected is None:
            await interaction.followup.send(
                "Please select a prediction first.", ephemeral=True
            )
            return

        embed = selected.get_embed(moderator=True)
        view = PredictionInteractionView(
            self.controller, interaction, selected, view_id, True
        )

        message = await interaction.followup.send(
            "", embed=embed, view=view, ephemeral=True
        )
        await view.set_message(message)
        await view.refresh_ui()

        event = UIEvent(UIEventType.PREDICTION_MODERATION_DISABLE, True, view_id)
        await self.controller.dispatch_ui_event(event)
