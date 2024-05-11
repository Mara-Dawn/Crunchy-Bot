import asyncio

import discord
from datalayer.database import Database
from datalayer.types import PredictionState, PredictionStateSort
from discord.ext import commands
from events.bot_event import BotEvent
from events.prediction_event import PredictionEvent
from events.types import EventType, PredictionEventType, UIEventType

# needed for global access
from events.ui_event import UIEvent
from items import *  # noqa: F403
from view.prediction.embed import PredictionEmbed
from view.prediction.info_view import PredictionInfoView
from view.prediction.moderation_embed import PredictionModerationEmbed
from view.prediction.moderation_view import PredictionModerationView
from view.prediction.overview_view import PredictionOverviewView
from view.prediction.view import PredictionView

from control.controller import Controller
from control.logger import BotLogger
from control.service import Service
from control.settings_manager import SettingsManager


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
                        | PredictionEventType.LOCK
                        | PredictionEventType.UNLOCK
                    ):
                        await self.refresh_prediction_messages(
                            prediction_event.guild_id
                        )
                    case PredictionEventType.SUBMIT | PredictionEventType.DENY:
                        return
                    case _:
                        prediction = await self.database.get_prediction_by_id(
                            prediction_event.prediction_id
                        )
                        prediction_stats = (
                            await self.database.get_prediction_stats_by_prediction(
                                prediction
                            )
                        )
                        event = UIEvent(
                            UIEventType.PREDICTION_OVERVIEW_REFRESH,
                            prediction_stats,
                        )
                        await self.controller.dispatch_ui_event(event)

    async def refresh_prediction_messages(self, guild_id: int):
        prediction_channels = await self.settings_manager.get_predictions_channels(
            guild_id
        )

        prediction_stats = await self.database.get_prediction_stats_by_guild(
            guild_id, [PredictionState.APPROVED, PredictionState.LOCKED]
        )

        prediction_stats = sorted(
            prediction_stats,
            key=lambda x: (
                PredictionStateSort.get_prio(x.prediction.state),
                x.prediction.get_timestamp_sort(),
                -x.prediction.id,
            ),
        )

        guild = self.bot.get_guild(guild_id)

        for channel_id in prediction_channels:
            channel = guild.get_channel(channel_id)
            if channel is None:
                continue

            await channel.purge()

            await self.database.clear_prediction_overview_messages(channel_id)

            author_name = self.bot.user.display_name
            author_img = self.bot.user.display_avatar
            head_embed = PredictionEmbed(author_name, author_img, guild.name)
            head_view = PredictionInfoView(self.controller)
            message = await channel.send(content="", embed=head_embed, view=head_view)
            head_view.set_message(message)

            for stats in prediction_stats:
                await asyncio.sleep(2)  # avoid rate limiting
                view = PredictionOverviewView(self.controller, stats)
                message = await channel.send(content="", view=view)
                view.set_message(message)
                await view.refresh_ui()
                await self.database.add_prediction_overview_message(
                    stats.prediction.id, message.id, channel_id
                )

    async def init_existing_prediction_messages(self, guild_id: int):

        prediction_stats = await self.database.get_prediction_stats_by_guild(
            guild_id, [PredictionState.APPROVED, PredictionState.LOCKED]
        )

        prediction_channels = await self.settings_manager.get_predictions_channels(
            guild_id
        )

        guild = self.bot.get_guild(guild_id)

        for channel_id in prediction_channels:
            channel = guild.get_channel(channel_id)
            if channel is None:
                continue

            async for message in channel.history(limit=1, oldest_first=True):
                if message.author != self.bot.user or message.embeds is None:
                    await self.refresh_prediction_messages(guild_id)
                    return

                embed_title = message.embeds[0].title
                if embed_title[:16] != "Bean Predictions":
                    await self.refresh_prediction_messages(guild_id)
                    return

                head_view = PredictionInfoView(self.controller)
                self.bot.add_view(head_view, message_id=message.id)
                head_view.set_message(message)
                head_view.reload_elements()
                author_name = self.bot.user.display_name
                author_img = self.bot.user.display_avatar
                head_embed = PredictionEmbed(author_name, author_img, guild.name)
                await message.edit(embed=head_embed)
                break

            for stats in prediction_stats:
                await asyncio.sleep(5)  # avoid rate limiting
                message_id = await self.database.get_prediction_overview_message(
                    stats.prediction.id, channel_id
                )
                if message_id is None:
                    await self.refresh_prediction_messages(guild_id)
                    return

                try:
                    message = await channel.fetch_message(message_id)
                except (discord.NotFound, discord.HTTPException):
                    await self.refresh_prediction_messages(guild_id)
                    return

                view = PredictionOverviewView(self.controller, stats)
                self.bot.add_view(view, message_id=message_id)

                view.set_message(message)
                await view.refresh_ui()

    async def post_prediction_interface(
        self, interaction: discord.Interaction, prediction_id: int = None
    ):
        await interaction.response.defer(ephemeral=True)

        prediction_stats = await self.database.get_prediction_stats_by_guild(
            interaction.guild_id, [PredictionState.APPROVED, PredictionState.LOCKED]
        )
        user_balance = await self.database.get_member_beans(
            interaction.guild.id, interaction.user.id
        )
        user_bets = await self.database.get_prediction_bets_by_user(
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

        prediction_stats = await self.database.get_prediction_stats_by_guild(
            interaction.guild_id
        )

        author_name = self.bot.user.display_name
        author_img = self.bot.user.display_avatar
        embed = PredictionModerationEmbed(
            author_name, author_img, interaction.guild.name
        )

        view = PredictionModerationView(self.controller, interaction, prediction_stats)

        message = await interaction.followup.send(
            content="",
            embed=embed,
            view=view,
            ephemeral=True,
        )
        view.set_message(message)
        await view.refresh_ui()
