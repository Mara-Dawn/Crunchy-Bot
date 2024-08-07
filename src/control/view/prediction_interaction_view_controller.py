import contextlib
import datetime

import discord
from datalayer.database import Database
from datalayer.prediction import Prediction
from datalayer.types import PredictionState
from discord.ext import commands
from events.beans_event import BeansEvent
from events.bot_event import BotEvent
from events.prediction_event import PredictionEvent
from events.types import BeansEventType, EventType, PredictionEventType, UIEventType
from events.ui_event import UIEvent
from view.prediction.interaction_view import PredictionInteractionView

from control.controller import Controller
from control.event_manager import EventManager
from control.logger import BotLogger
from control.settings_manager import SettingsManager
from control.view.view_controller import ViewController


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

    async def listen_for_event(self, event: BotEvent) -> None:
        match event.type:
            case EventType.PREDICTION:
                prediction_event: PredictionEvent = event
                prediction = await self.database.get_prediction_by_id(
                    prediction_event.prediction_id
                )
                prediction_stats = (
                    await self.database.get_prediction_stats_by_prediction(prediction)
                )
                event = UIEvent(
                    UIEventType.PREDICTION_INTERACTION_REFRESH,
                    prediction_stats,
                )
                await self.controller.dispatch_ui_event(event)

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
            case UIEventType.PREDICTION_INTERACTION_UNLOCK:
                interaction = event.payload[0]
                prediction = event.payload[1]
                await self.unlock_prediction(interaction, prediction, event.view_id)
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
            case UIEventType.PREDICTION_INTERACTION_RESUBMIT:
                interaction = event.payload[0]
                prediction = event.payload[1]
                await self.resubmit_prediction(interaction, prediction, event.view_id)

    async def __refresh_view(
        self, interaction: discord.Interaction, prediction: Prediction, view_id: int
    ):
        view: PredictionInteractionView | None = self.controller.get_view(view_id)

        if view is None:
            with contextlib.suppress(discord.errors.NotFound):
                message = await interaction.original_response()
                await message.delete()

        prediction_stats = await self.database.get_prediction_stats_by_prediction(
            prediction
        )
        view.prediction_stats = prediction_stats

        await view.refresh_ui()

    async def confirm_outcome(
        self,
        interaction: discord.Interaction,
        prediction: Prediction,
        selected_outcome_id: int | None,
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

        await self.database.update_prediction(prediction)

        event = PredictionEvent(
            datetime.datetime.now(),
            guild_id,
            prediction.id,
            member_id,
            PredictionEventType.RESOLVE,
            selected_outcome_id,
        )
        await self.controller.dispatch_event(event)

        prediction_stats = await self.database.get_prediction_stats_by_prediction(
            prediction
        )
        winners = await self.database.get_prediction_bets_by_outcome(
            selected_outcome_id
        )
        odds = prediction_stats.get_odds(selected_outcome_id)
        odds_text = round(odds, 2)
        if int(odds) == odds:
            odds_text = int(odds)
        prediction_text = prediction.content
        outcome_text = prediction.outcomes[selected_outcome_id]
        for user_id, amount in winners.items():
            if user_id == self.bot.user.id:
                continue

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

        total = sum(prediction_stats.bets.values())

        author = self.bot.get_user(prediction.author_id)
        if author is not None and author.id != self.bot.user.id:
            payout = int(total * 0.05)
            event = BeansEvent(
                datetime.datetime.now(),
                guild_id,
                BeansEventType.PREDICTION_PAYOUT,
                author.id,
                payout,
            )
            await self.controller.dispatch_event(event)

            message = f"Your submitted prediction '**{prediction_text}**' has come to a close and the winners have been paid out! Here is your reward for a successfull submission:"
            message += f"```python\nTotal Pot: 🅱️{total}\nReward: 5%\n-----------------------\nPayout:🅱️{payout}```"
            await author.send(message)

        bean_channels = await self.settings_manager.get_beans_notification_channels(
            interaction.guild_id
        )
        announcement = (
            "**Prediction Results:\n**"
            f"The prediction '**{prediction_text}**' has come to a close!\n The winning outcome is '**{outcome_text}**' "
            f"with winning odds of 1:{odds_text}.\n A total of `🅱️{total}` has been paid out."
        )
        for channel_id in bean_channels:
            channel = interaction.guild.get_channel(channel_id)
            await channel.send(announcement)

        success_message = "You successfully resolved your selected Prediction. The winners were paid out."
        await interaction.followup.send(success_message, ephemeral=True)

        await self.__refresh_view(interaction, prediction, view_id)

    async def deny_submission(
        self, interaction: discord.Interaction, prediction: Prediction, view_id: int
    ):
        guild_id = interaction.guild_id
        member_id = interaction.user.id

        prediction.state = PredictionState.DENIED
        prediction.moderator_id = member_id

        await self.database.update_prediction(prediction)

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

        await self.__refresh_view(interaction, prediction, view_id)

    async def lock_prediction(
        self, interaction: discord.Interaction, prediction: Prediction, view_id: int
    ):
        guild_id = interaction.guild_id
        member_id = interaction.user.id

        prediction.state = PredictionState.LOCKED
        prediction.moderator_id = member_id

        await self.database.update_prediction(prediction)

        event = PredictionEvent(
            datetime.datetime.now(),
            guild_id,
            prediction.id,
            member_id,
            PredictionEventType.LOCK,
        )
        await self.controller.dispatch_event(event)

        bean_channels = await self.settings_manager.get_beans_notification_channels(
            interaction.guild_id
        )
        announcement = (
            f"**This prediction has been locked in!**\n> {prediction.content}\nNo more bets will be accepted. "
            "The winners will be paid out once an outcome is achieved. Good luck!\nYou can also submit your own "
            "prediction ideas in the overview channel."
        )
        for channel_id in bean_channels:
            channel = interaction.guild.get_channel(channel_id)
            await channel.send(announcement)

        success_message = "You successfully locked your selected prediction submission."
        await interaction.followup.send(success_message, ephemeral=True)

        await self.__refresh_view(interaction, prediction, view_id)

    async def unlock_prediction(
        self, interaction: discord.Interaction, prediction: Prediction, view_id: int
    ):
        guild_id = interaction.guild_id
        member_id = interaction.user.id

        prediction.state = PredictionState.APPROVED
        prediction.moderator_id = member_id

        await self.database.update_prediction(prediction)

        event = PredictionEvent(
            datetime.datetime.now(),
            guild_id,
            prediction.id,
            member_id,
            PredictionEventType.UNLOCK,
        )
        await self.controller.dispatch_event(event)

        bean_channels = await self.settings_manager.get_beans_notification_channels(
            interaction.guild_id
        )
        announcement = (
            f"**This prediction has been unlocked again!**\n> {prediction.content}\n"
            "You can start betting on it again for now. Good luck!\n"
            "You can also submit your own prediction ideas in the overview channel."
        )
        for channel_id in bean_channels:
            channel = interaction.guild.get_channel(channel_id)
            await channel.send(announcement)

        success_message = (
            "You successfully unlocked your selected prediction submission."
        )
        await interaction.followup.send(success_message, ephemeral=True)

        await self.__refresh_view(interaction, prediction, view_id)

    async def approve_submission(
        self, interaction: discord.Interaction, prediction: Prediction, view_id: int
    ):
        guild_id = interaction.guild_id
        member_id = interaction.user.id

        prediction.state = PredictionState.APPROVED
        prediction.moderator_id = member_id

        await self.database.update_prediction(prediction)

        event = PredictionEvent(
            datetime.datetime.now(),
            guild_id,
            prediction.id,
            member_id,
            PredictionEventType.APPROVE,
        )
        await self.controller.dispatch_event(event)

        base_pot = 1000
        outcome_count = len(prediction.outcomes)
        outcome_base_pot = int(base_pot / outcome_count)

        for outcome_id in prediction.outcomes:
            event = PredictionEvent(
                datetime.datetime.now(),
                guild_id,
                prediction.id,
                self.bot.user.id,
                PredictionEventType.PLACE_BET,
                outcome_id,
                outcome_base_pot,
            )
            await self.controller.dispatch_event(event)

        bean_channels = await self.settings_manager.get_beans_notification_channels(
            interaction.guild_id
        )
        announcement = (
            f"**A new prediction has been approved!**\n> {prediction.content}\n"
            "Use `/beans prediction` to bet your beans on the outcomes. "
            "You can also submit your own prediction ideas in the overview channel."
        )
        for channel_id in bean_channels:
            channel = interaction.guild.get_channel(channel_id)
            await channel.send(announcement)

        success_message = (
            "You successfully approved your selected prediction submission."
        )
        await interaction.followup.send(success_message, ephemeral=True)

        await self.__refresh_view(interaction, prediction, view_id)

    async def resubmit_prediction(
        self,
        interaction: discord.Interaction,
        prediction: Prediction,
        view_id: int,
    ):
        prediction.author_id = self.bot.user.id
        prediction_id = await self.database.log_prediction(prediction)
        event = PredictionEvent(
            datetime.datetime.now(),
            prediction.guild_id,
            prediction_id,
            prediction.author_id,
            PredictionEventType.SUBMIT,
        )
        await self.controller.dispatch_event(event)

        new_prediction = await self.database.get_prediction_by_id(prediction_id)

        success_message = "You successfully resubmitted your selected prediction."
        await interaction.followup.send(success_message, ephemeral=True)

        await self.__refresh_view(interaction, new_prediction, view_id)

    async def edit_prediction(
        self,
        interaction: discord.Interaction,
        updated_prediction: Prediction,
        view_id: int,
    ):
        guild_id = interaction.guild_id
        member_id = interaction.user.id

        await self.database.update_prediction(updated_prediction)

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

        await self.__refresh_view(interaction, updated_prediction, view_id)

    async def end_and_refund_submission(
        self, interaction: discord.Interaction, prediction: Prediction, view_id: int
    ):
        guild_id = interaction.guild_id
        member_id = interaction.user.id

        prediction.state = PredictionState.REFUNDED
        prediction.moderator_id = member_id

        await self.database.update_prediction(prediction)

        event = PredictionEvent(
            datetime.datetime.now(),
            guild_id,
            prediction.id,
            member_id,
            PredictionEventType.REFUND,
        )
        await self.controller.dispatch_event(event)

        data = await self.database.get_prediction_bets_by_id(prediction.id)

        for user_id, amount in data.items():
            if user_id == self.bot.user.id:
                continue
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

        await self.__refresh_view(interaction, prediction, view_id)
