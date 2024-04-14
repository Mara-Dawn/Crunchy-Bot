import discord
from discord.ext import commands

from control.controller import Controller
from control.logger import BotLogger
from control.service import Service
from control.settings_manager import SettingsManager
from datalayer.database import Database
from datalayer.types import PredictionState
from events.bot_event import BotEvent
from events.prediction_event import PredictionEvent
from events.types import EventType, PredictionEventType, UIEventType

# needed for global access
from events.ui_event import UIEvent
from items import *  # noqa: F403
from view.prediction_embed import PredictionEmbed
from view.prediction_info_view import PredictionInfoView
from view.prediction_moderation_embed import PredictionModerationEmbed
from view.prediction_moderation_view import PredictionModerationView
from view.prediction_overview_view import PredictionOverviewView
from view.prediction_view import PredictionView


class PredictionManager(Service):

    def __init__(
        self,
        bot: commands.Bot,
        logger: BotLogger,
        database: Database,
        controller: Controller,
    ):
        super().__init__(bot, logger, database)
        self.controller = controller
        self.settings_manager: SettingsManager = self.controller.get_service(
            SettingsManager
        )
        self.log_name = "Predictions"

    async def listen_for_event(self, event: BotEvent):
        match event.type:
            case EventType.PREDICTION:
                prediction_event: PredictionEvent = event

                match prediction_event.prediction_event_type:
                    case (
                        PredictionEventType.APPROVE
                        | PredictionEventType.RESOLVE
                        | PredictionEventType.REFUND
                    ):
                        await self.refresh_prediction_messages(
                            prediction_event.guild_id
                        )
                    case PredictionEventType.SUBMIT | PredictionEventType.DENY:
                        return
                    case _:
                        prediction = self.database.get_prediction_by_id(
                            prediction_event.prediction_id
                        )
                        prediction_stats = (
                            self.database.get_prediction_stats_by_prediction(prediction)
                        )
                        event = UIEvent(
                            UIEventType.PREDICTION_OVERVIEW_REFRESH,
                            prediction_stats,
                        )
                        await self.controller.dispatch_ui_event(event)

    async def refresh_prediction_messages(self, guild_id: int):
        prediction_channels = self.settings_manager.get_predictions_channels(guild_id)

        prediction_stats = self.database.get_prediction_stats_by_guild(
            guild_id, [PredictionState.APPROVED, PredictionState.LOCKED]
        )

        guild = self.bot.get_guild(guild_id)

        for channel_id in prediction_channels:
            channel = guild.get_channel(channel_id)
            if channel is None:
                continue

            await channel.purge()
            head_embed = PredictionEmbed(guild.name)
            head_view = PredictionInfoView(self.controller)
            message = await channel.send(content="", embed=head_embed, view=head_view)
            head_view.set_message(message)

            for stats in prediction_stats:
                view = PredictionOverviewView(self.controller, stats)
                message = await channel.send(content="", view=view)
                view.set_message(message)
                await view.refresh_ui()

    async def post_prediction_interface(
        self, interaction: discord.Interaction, prediction_id: int = None
    ):
        await interaction.response.defer(ephemeral=True)

        prediction_stats = self.database.get_prediction_stats_by_guild(
            interaction.guild_id, [PredictionState.APPROVED, PredictionState.LOCKED]
        )
        user_balance = self.database.get_member_beans(
            interaction.guild.id, interaction.user.id
        )
        user_bets = self.database.get_prediction_bets_by_user(
            interaction.guild.id, interaction.user.id
        )

        view = PredictionView(
            self.controller, interaction, prediction_stats, selected=prediction_id
        )

        message = await interaction.followup.send(
            content="",
            view=view,
            ephemeral=True,
        )
        view.set_message(message)
        await view.refresh_ui(user_balance=user_balance, user_bets=user_bets)

    async def post_prediction_moderation_interface(
        self, interaction: discord.Interaction
    ):
        await interaction.response.defer(ephemeral=True)

        prediction_stats = self.database.get_prediction_stats_by_guild(
            interaction.guild_id
        )

        embed = PredictionModerationEmbed(interaction.guild.name)

        view = PredictionModerationView(self.controller, interaction, prediction_stats)

        message = await interaction.followup.send(
            content="",
            embed=embed,
            view=view,
            ephemeral=True,
        )
        view.set_message(message)
        await view.refresh_ui()
