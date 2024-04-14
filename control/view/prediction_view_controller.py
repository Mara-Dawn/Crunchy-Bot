import datetime

import discord
from discord.ext import commands

from control.controller import Controller
from control.logger import BotLogger
from control.prediction_manager import PredictionManager
from control.view.view_controller import ViewController
from datalayer.database import Database
from datalayer.prediction import Prediction
from datalayer.types import PredictionState
from events.beans_event import BeansEvent
from events.bot_event import BotEvent
from events.prediction_event import PredictionEvent
from events.types import (
    BeansEventType,
    EventType,
    PredictionEventType,
    UIEventType,
)
from events.ui_event import UIEvent


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
        self.prediction_manager: PredictionManager = self.controller.get_service(
            PredictionManager
        )

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
            case UIEventType.PREDICTION_PLACE_BET:
                interaction = event.payload[0]
                prediction = event.payload[1]
                selected_outcome = event.payload[2]
                selected_bet_amount = event.payload[3]
                await self.submit_bet(
                    interaction,
                    prediction,
                    selected_outcome,
                    selected_bet_amount,
                    event.view_id,
                )
            case UIEventType.PREDICTION_OPEN_UI:
                interaction = event.payload[0]
                prediction: Prediction = event.payload[1]
                if prediction is None:
                    await self.open_ui(interaction, None)
                    return
                await self.open_ui(interaction, prediction.id)
            case UIEventType.PREDICTION_PREDICTION_SUBMIT:
                await self.submit_prediction(event.payload)

    async def open_ui(self, interaction: discord.Interaction, prediction_id: int):
        await self.prediction_manager.post_prediction_interface(
            interaction, prediction_id
        )

    async def submit_prediction(self, prediction: Prediction):
        prediction_id = self.database.log_prediction(prediction)
        event = PredictionEvent(
            datetime.datetime.now(),
            prediction.guild_id,
            prediction_id,
            prediction.author_id,
            PredictionEventType.SUBMIT,
        )
        await self.controller.dispatch_event(event)

    async def submit_bet(
        self,
        interaction: discord.Interaction,
        prediction: Prediction,
        selected_outcome_id: int,
        selected_bet_amount: int,
        view_id: int,
    ):
        guild_id = interaction.guild_id
        member_id = interaction.user.id

        user_bets = self.database.get_prediction_bets_by_user(
            interaction.guild_id, interaction.user.id
        )

        if prediction.id in user_bets:
            user_prediction_bets = user_bets[prediction.id]
            if user_prediction_bets[0] != selected_outcome_id:
                await interaction.followup.send(
                    "You cannot bet on other outcomes once you placed your bet for a prediction.\nYou may bet additional beans on your previously selected outcome though.\nUse `/beans prediction` for a better overview of your current bets.",
                    ephemeral=True,
                )
                return

        if prediction is None:
            await interaction.followup.send(
                "Please select a prediction first.", ephemeral=True
            )
            return

        if prediction.state == PredictionState.LOCKED:
            await interaction.followup.send(
                "This prediction is already locked in.", ephemeral=True
            )
            return

        if selected_outcome_id is None:
            await interaction.followup.send("Please select an outcome.", ephemeral=True)
            return False

        if selected_bet_amount is None or int(selected_bet_amount) <= 0:
            await interaction.followup.send(
                "Please place your bet first.", ephemeral=True
            )
            return False

        user_balance = self.database.get_member_beans(guild_id, member_id)

        if user_balance < selected_bet_amount:
            await interaction.followup.send(
                "You dont have enough beans for this bet.", ephemeral=True
            )
            return False

        timestamp = datetime.datetime.now()

        event = PredictionEvent(
            timestamp,
            guild_id,
            prediction.id,
            member_id,
            PredictionEventType.PLACE_BET,
            selected_outcome_id,
            selected_bet_amount,
        )
        await self.controller.dispatch_event(event)

        event = BeansEvent(
            timestamp,
            guild_id,
            BeansEventType.PREDICTION_BET,
            member_id,
            -selected_bet_amount,
        )
        await self.controller.dispatch_event(event)
