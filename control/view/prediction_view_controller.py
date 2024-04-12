import discord
from discord.ext import commands

from control.controller import Controller
from control.logger import BotLogger
from control.view.view_controller import ViewController
from datalayer.database import Database
from datalayer.prediction_stats import PredictionStats
from datalayer.types import PredictionState
from events.beans_event import BeansEvent
from events.bot_event import BotEvent
from events.prediction_event import PredictionEvent
from events.types import (
    EventType,
    PredictionEventType,
    UIEventType,
)
from events.ui_event import UIEvent
from view.prediction_interaction_view import PredictionInteractionView


class PredictionViewController(ViewController):

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
                    UIEventType.PREDICTION_REFRESH_ALL,
                    prediction_stats,
                )
                await self.controller.dispatch_ui_event(event)

                if (
                    prediction_event.prediction_event_type
                    == PredictionEventType.PLACE_BET
                ):
                    user_bets = self.database.get_prediction_bets_by_user(
                        prediction_event.guild_id, prediction_event.member_id
                    )
                    user_balance = self.database.get_member_beans(
                        prediction_event.guild_id, prediction_event.member_id
                    )
                    event = UIEvent(
                        UIEventType.PREDICTION_BET_REFRESH,
                        (prediction_event.member_id, user_bets, user_balance),
                    )
                    await self.controller.dispatch_ui_event(event)
            case EventType.BEANS:
                beans_event: BeansEvent = event
                if beans_event.value == 0:
                    return
                new_user_balance = self.database.get_member_beans(
                    beans_event.guild_id, beans_event.member_id
                )
                event = UIEvent(
                    UIEventType.PREDICTION_USER_REFRESH,
                    (beans_event.member_id, new_user_balance),
                )
                await self.controller.dispatch_ui_event(event)

    async def listen_for_ui_event(self, event: UIEvent):
        match event.type:
            case UIEventType.PREDICTION_SELECT:
                interaction = event.payload[0]
                selected_prediction = event.payload[1]
                await self.select(interaction, selected_prediction, event.view_id)
            case (
                UIEventType.PREDICTION_CHANGED
                | UIEventType.PREDICTION_INTERACTION_PARENT_CHANGED
            ):
                guild_id = event.payload
                prediction_stats = self.database.get_prediction_stats_by_guild(guild_id)
                event = UIEvent(
                    UIEventType.PREDICTION_REFRESH, prediction_stats, event.view_id
                )
                await self.controller.dispatch_ui_event(event)

    async def select(
        self, interaction: discord.Interaction, selected: PredictionStats, view_id: int
    ):
        if selected is None:
            await interaction.followup.send(
                "Please select a prediction first.", ephemeral=True
            )
            return

        if selected.prediction.state == PredictionState.LOCKED:
            await interaction.followup.send(
                "This prediction is already locked in.", ephemeral=True
            )
            return

        view = PredictionInteractionView(
            self.controller, interaction, selected, view_id, False
        )

        message = await interaction.original_response()

        await message.edit(view=view)

        await view.set_message(message)
        await view.refresh_ui()
