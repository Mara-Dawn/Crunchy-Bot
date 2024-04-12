import datetime

import discord
from discord.ext import commands

from control.controller import Controller
from control.event_manager import EventManager
from control.logger import BotLogger
from control.settings_manager import SettingsManager
from control.view.view_controller import ViewController
from datalayer.database import Database
from datalayer.prediction import Prediction
from datalayer.types import PredictionState
from events.beans_event import BeansEvent
from events.prediction_event import PredictionEvent
from events.types import BeansEventType, PredictionEventType, UIEventType
from events.ui_event import UIEvent
from view.prediction_view import PredictionView


class PredictionInteractionViewController(ViewController):

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
        self.event_manager: EventManager = controller.get_service(EventManager)
        self.settings_manager: SettingsManager = controller.get_service(SettingsManager)

    async def listen_for_ui_event(self, event: UIEvent):
        match event.type:
            case UIEventType.PREDICTION_INTERACTION_CONFIRM_OUTCOME:
                interaction = event.payload[0]
                prediction = event.payload[1]
                selected_outcome_id = event.payload[2]
                await self.confirm_outcome(
                    interaction, prediction, selected_outcome_id, event.view_id
                )
            case UIEventType.PREDICTION_INTERACTION_DENY:
                interaction = event.payload[0]
                prediction = event.payload[1]
                await self.deny_submission(interaction, prediction, event.view_id)
            case UIEventType.PREDICTION_INTERACTION_APPROVE:
                interaction = event.payload[0]
                prediction = event.payload[1]
                await self.approve_submission(interaction, prediction, event.view_id)
            case UIEventType.PREDICTION_INTERACTION_LOCK:
                interaction = event.payload[0]
                prediction = event.payload[1]
                await self.lock_prediction(interaction, prediction, event.view_id)
            case UIEventType.PREDICTION_INTERACTION_EDIT:
                interaction = event.payload[0]
                new_prediction = event.payload[1]
                await self.edit_prediction(interaction, new_prediction, event.view_id)
            case UIEventType.PREDICTION_INTERACTION_REFUND:
                interaction = event.payload[0]
                prediction = event.payload[1]
                await self.end_and_refund_submission(
                    interaction, prediction, event.view_id
                )
            case UIEventType.PREDICTION_INTERACTION_PLACE_BET:
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
            case UIEventType.PREDICTION_INTERACTION_CANCEL:
                interaction = event.payload
                await self.cancel_interaction(
                    interaction,
                    event.view_id,
                )

    async def cancel_interaction(
        self,
        interaction: discord.Interaction,
        view_id: int,
    ):
        message = await interaction.original_response()

        prediction_stats = self.database.get_prediction_stats_by_guild(
            interaction.guild_id, [PredictionState.APPROVED]
        )
        user_balance = self.database.get_member_beans(
            interaction.guild.id, interaction.user.id
        )
        user_bets = self.database.get_prediction_bets_by_user(
            interaction.guild.id, interaction.user.id
        )

        view = self.controller.get_view(view_id)
        if view is None:
            view = PredictionView(self.controller, interaction, prediction_stats)

        await message.edit(view=view)

        view.set_message(message)
        await view.refresh_ui(user_balance=user_balance, user_bets=user_bets)

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

        prediction_stats = self.database.get_prediction_stats_by_guild(
            interaction.guild_id, [PredictionState.APPROVED]
        )
        user_balance = self.database.get_member_beans(
            interaction.guild.id, interaction.user.id
        )
        user_bets = self.database.get_prediction_bets_by_user(
            interaction.guild.id, interaction.user.id
        )

        message = await interaction.original_response()

        view = self.controller.get_view(view_id)
        if view is None:
            view = PredictionView(self.controller, interaction, prediction_stats)

        await message.edit(view=view)

        view.set_message(message)
        await view.refresh_ui(user_balance=user_balance, user_bets=user_bets)

    async def confirm_outcome(
        self,
        interaction: discord.Interaction,
        prediction: Prediction,
        selected_outcome_id: int,
        view_id: int,
    ):
        guild_id = interaction.guild_id
        member_id = interaction.user.id

        if selected_outcome_id is None:
            await interaction.followup.send(
                "Please select an outcome first.", ephemeral=True
            )
            return False

        prediction.state = PredictionState.DONE
        prediction.moderator_id = member_id

        self.database.update_prediction(prediction)

        event = PredictionEvent(
            datetime.datetime.now(),
            guild_id,
            prediction.id,
            member_id,
            PredictionEventType.RESOLVE,
            selected_outcome_id,
        )
        await self.controller.dispatch_event(event)

        prediction_stats = self.database.get_prediction_stats_by_prediction(prediction)
        winners = self.database.get_prediction_bets_by_outcome(selected_outcome_id)
        odds = prediction_stats.get_odds(selected_outcome_id)
        odds_text = round(odds, 2)
        if int(odds) == odds:
            odds_text = int(odds)
        prediction_text = prediction.content
        outcome_text = prediction.outcomes[selected_outcome_id]
        for user_id, amount in winners.items():
            payout = int(amount * odds)
            event = BeansEvent(
                datetime.datetime.now(),
                guild_id,
                BeansEventType.PREDICTION_PAYOUT,
                user_id,
                payout,
            )
            await self.controller.dispatch_event(event)

            user = self.bot.get_user(user_id)

            if user is not None:
                message = f"Congratulations, you correclty predicted the outcome '**{outcome_text}**' for '**{prediction_text}**' on {interaction.guild.name}!"
                message += f"```python\nInitial bet: 🅱️{amount}\nOdds: 1:{odds_text}\n-----------------------\nPayout:🅱️{payout}```"
                await user.send(message)

        bean_channels = self.settings_manager.get_beans_channels(interaction.guild_id)
        announcement = f"The prediction '**{prediction_text}**' has come to a close!\n The winning outcome is '**{outcome_text}**' with winning odds of 1:{odds_text}.\n A total of `🅱️{sum(prediction_stats.bets.values())}` has been paid out."
        for channel_id in bean_channels:
            channel = interaction.guild.get_channel(channel_id)
            await channel.send(announcement)

        success_message = "You successfully resolved your selected Prediction. The winners were paid out."
        await interaction.followup.send(success_message, ephemeral=True)

        prediction = self.database.get_prediction_stats_by_guild(guild_id)
        event = UIEvent(UIEventType.PREDICTION_MODERATION_REFRESH, prediction, view_id)
        await self.controller.dispatch_ui_event(event)

        message = await interaction.original_response()
        await message.delete()

    async def deny_submission(
        self, interaction: discord.Interaction, prediction: Prediction, view_id: int
    ):
        guild_id = interaction.guild_id
        member_id = interaction.user.id

        prediction.state = PredictionState.DENIED
        prediction.moderator_id = member_id

        self.database.update_prediction(prediction)

        event = PredictionEvent(
            datetime.datetime.now(),
            guild_id,
            prediction.id,
            member_id,
            PredictionEventType.DENY,
        )
        await self.controller.dispatch_event(event)

        success_message = "You successfully denied your selected prediction submission."
        await interaction.followup.send(success_message, ephemeral=True)

        prediction = self.database.get_prediction_stats_by_guild(guild_id)
        event = UIEvent(UIEventType.PREDICTION_MODERATION_REFRESH, prediction, view_id)
        await self.controller.dispatch_ui_event(event)

        message = await interaction.original_response()
        await message.delete()

    async def lock_prediction(
        self, interaction: discord.Interaction, prediction: Prediction, view_id: int
    ):
        guild_id = interaction.guild_id
        member_id = interaction.user.id

        prediction.state = PredictionState.LOCKED
        prediction.moderator_id = member_id

        self.database.update_prediction(prediction)

        event = PredictionEvent(
            datetime.datetime.now(),
            guild_id,
            prediction.id,
            member_id,
            PredictionEventType.LOCK,
        )
        await self.controller.dispatch_event(event)

        bean_channels = self.settings_manager.get_beans_channels(interaction.guild_id)
        announcement = f"**This predicktion has been locked in!**\n> {prediction.content}\nNo more bets will be accepted. The winners will be paid out once an outcome is achieved. Good luck!\nYou can also submit your own prediction ideas in the `/shop`."
        for channel_id in bean_channels:
            channel = interaction.guild.get_channel(channel_id)
            await channel.send(announcement)

        success_message = "You successfully locked your selected prediction submission."
        await interaction.followup.send(success_message, ephemeral=True)

        prediction = self.database.get_prediction_stats_by_guild(guild_id)
        event = UIEvent(UIEventType.PREDICTION_MODERATION_REFRESH, prediction, view_id)
        await self.controller.dispatch_ui_event(event)

        message = await interaction.original_response()
        await message.delete()

    async def approve_submission(
        self, interaction: discord.Interaction, prediction: Prediction, view_id: int
    ):
        guild_id = interaction.guild_id
        member_id = interaction.user.id

        prediction.state = PredictionState.APPROVED
        prediction.moderator_id = member_id

        self.database.update_prediction(prediction)

        event = PredictionEvent(
            datetime.datetime.now(),
            guild_id,
            prediction.id,
            member_id,
            PredictionEventType.APPROVE,
        )
        await self.controller.dispatch_event(event)

        bean_channels = self.settings_manager.get_beans_channels(interaction.guild_id)
        announcement = f"**A new prediction has been approved!**\n> {prediction.content}\nUse `/beans prediction` to bet your beans on the outcomes. You can also submit your own prediction ideas in the `/shop`."
        for channel_id in bean_channels:
            channel = interaction.guild.get_channel(channel_id)
            await channel.send(announcement)

        success_message = (
            "You successfully approved your selected prediction submission."
        )
        await interaction.followup.send(success_message, ephemeral=True)

        prediction = self.database.get_prediction_stats_by_guild(guild_id)
        event = UIEvent(UIEventType.PREDICTION_MODERATION_REFRESH, prediction, view_id)
        await self.controller.dispatch_ui_event(event)

        message = await interaction.original_response()
        await message.delete()

    async def edit_prediction(
        self,
        interaction: discord.Interaction,
        updated_prediction: Prediction,
        view_id: int,
    ):
        guild_id = interaction.guild_id
        member_id = interaction.user.id

        self.database.update_prediction(updated_prediction)

        event = PredictionEvent(
            datetime.datetime.now(),
            guild_id,
            updated_prediction.id,
            member_id,
            PredictionEventType.EDIT,
        )
        await self.controller.dispatch_event(event)

        success_message = (
            "You successfully made changes to your selected prediction submission."
        )
        await interaction.followup.send(success_message, ephemeral=True)

        updated_prediction = self.database.get_prediction_stats_by_guild(guild_id)
        event = UIEvent(
            UIEventType.PREDICTION_MODERATION_REFRESH, updated_prediction, view_id
        )
        await self.controller.dispatch_ui_event(event)

        message = await interaction.original_response()
        await message.delete()

    async def end_and_refund_submission(
        self, interaction: discord.Interaction, prediction: Prediction, view_id: int
    ):
        guild_id = interaction.guild_id
        member_id = interaction.user.id

        prediction.state = PredictionState.REFUNDED
        prediction.moderator_id = member_id

        self.database.update_prediction(prediction)

        event = PredictionEvent(
            datetime.datetime.now(),
            guild_id,
            prediction.id,
            member_id,
            PredictionEventType.REFUND,
        )
        await self.controller.dispatch_event(event)

        data = self.database.get_prediction_bets_by_id(prediction.id)

        for user_id, amount in data.items():
            event = BeansEvent(
                datetime.datetime.now(),
                guild_id,
                BeansEventType.PREDICTION_REFUND,
                user_id,
                amount,
            )
            await self.controller.dispatch_event(event)

            user = self.bot.get_user(user_id)

            if user is not None:
                message = f"Your bet for your prediction of '**{prediction.content}**' was refunded by a moderator, `🅱️{amount}` have been transferred back to your beans account on {interaction.guild.name}"
                await user.send(message)

        success_message = (
            "You successfully ended and refunded your selected prediction submission."
        )
        await interaction.followup.send(success_message, ephemeral=True)

        prediction = self.database.get_prediction_stats_by_guild(guild_id)
        event = UIEvent(UIEventType.PREDICTION_MODERATION_REFRESH, prediction, view_id)
        await self.controller.dispatch_ui_event(event)

        message = await interaction.original_response()
        await message.delete()
