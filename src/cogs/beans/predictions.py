import datetime
from typing import Literal

import discord
from control.settings_manager import SettingsManager
from datalayer.types import PredictionState
from discord import app_commands
from discord.ext import commands, tasks
from events.prediction_event import PredictionEvent
from events.types import PredictionEventType

from cogs.beans.beans_group import BeansGroup


class Predictions(BeansGroup):

    @staticmethod
    async def __has_permission(interaction: discord.Interaction) -> bool:
        author_id = 90043934247501824
        return (
            interaction.user.id == author_id
            or interaction.user.guild_permissions.administrator
        )

    def __has_mod_permission(self, interaction: discord.Interaction) -> bool:
        author_id = 90043934247501824
        roles = self.settings_manager.get_predictions_mod_roles(interaction.guild_id)
        is_mod = (
            len(set([x.id for x in interaction.user.roles]).intersection(roles)) > 0
        )
        return (
            interaction.user.id == author_id
            or interaction.user.guild_permissions.administrator
            or is_mod
        )

    async def __check_enabled(
        self, interaction: discord.Interaction, all_channels: bool = False
    ):
        guild_id = interaction.guild_id

        if not self.settings_manager.get_predictions_enabled(guild_id):
            await self.bot.command_response(
                self.__cog_name__,
                interaction,
                "Beans predictions module is currently disabled.",
            )
            return False

        if (
            not all_channels
            and interaction.channel_id
            not in self.settings_manager.get_beans_channels(guild_id)
        ):
            await self.bot.command_response(
                self.__cog_name__,
                interaction,
                "Prediction commands cannot be used in this channel.",
            )
            return False

        return True

    @commands.Cog.listener("on_ready")
    async def on_ready_prediction(self) -> None:
        self.prediction_timeout_check.start()

        for guild in self.bot.guilds:
            await self.prediction_manager.init_existing_prediction_messages(guild.id)

        self.logger.log("init", "Predictions loaded.", cog=self.__cog_name__)

    @tasks.loop(seconds=60)
    async def prediction_timeout_check(self):
        self.logger.debug(
            "sys", "prediction timeout check task started", cog=self.__cog_name__
        )

        for guild in self.bot.guilds:
            guild_id = guild.id
            self.logger.debug(
                guild_id,
                f"prediction timeout for guild {guild.name}.",
                cog=self.__cog_name__,
            )

            active_predictions = self.database.get_predictions_by_guild(
                guild_id, [PredictionState.APPROVED]
            )

            if active_predictions is None:
                continue

            for prediction in active_predictions:
                time_now = datetime.datetime.now()
                lock_in_datetime = prediction.lock_datetime

                if lock_in_datetime is None:
                    continue

                remainder = lock_in_datetime - time_now
                remainder = int(max(remainder.total_seconds() / 60, 0))

                self.logger.debug(
                    guild_id,
                    f"prediction timeout check for {prediction.content}. Remaining: {remainder}",
                    cog=self.__cog_name__,
                )

                if time_now > lock_in_datetime:

                    prediction.state = PredictionState.LOCKED
                    prediction.lock_datetime = None
                    self.database.update_prediction(prediction)

                    event = PredictionEvent(
                        datetime.datetime.now(),
                        guild_id,
                        prediction.id,
                        self.bot.user.id,
                        PredictionEventType.LOCK,
                    )
                    await self.controller.dispatch_event(event)

                    bean_channels = (
                        self.settings_manager.get_beans_notification_channels(guild_id)
                    )
                    announcement = (
                        f"**This prediction has been locked in!**\n> {prediction.content}\nNo more bets will be accepted. "
                        "The winners will be paid out once an outcome is achieved. Good luck!\nYou can also submit your own "
                        "prediction ideas in the overview channel or in the `/shop`."
                    )
                    for channel_id in bean_channels:
                        channel = guild.get_channel(channel_id)
                        await channel.send(announcement)

    @app_commands.command(
        name="prediction", description="Bet your beans on various predictions."
    )
    @app_commands.guild_only()
    async def prediction(self, interaction: discord.Interaction):
        if not await self.__check_enabled(interaction):
            return

        log_message = (
            f"{interaction.user.name} used command `{interaction.command.name}`."
        )
        self.logger.log(interaction.guild_id, log_message, cog=self.__cog_name__)
        await self.prediction_manager.post_prediction_interface(interaction)

    @app_commands.command(
        name="prediction_moderation",
        description="Prediction moderation interface.",
    )
    @app_commands.guild_only()
    async def prediction_moderation(self, interaction: discord.Interaction):
        if not await self.__check_enabled(interaction, all_channels=True):
            return

        if not self.__has_mod_permission(interaction):
            raise app_commands.MissingPermissions([])

        log_message = (
            f"{interaction.user.name} used command `{interaction.command.name}`."
        )
        self.logger.log(interaction.guild_id, log_message, cog=self.__cog_name__)
        await self.prediction_manager.post_prediction_moderation_interface(interaction)

    group = app_commands.Group(
        name="predictions", description="Subcommands for the Beans Predictions module."
    )

    @group.command(
        name="reload_overview",
        description="Reloads prediction overview.",
    )
    @app_commands.guild_only()
    async def reload_overview(self, interaction: discord.Interaction):
        if not await self.__check_enabled(interaction, all_channels=True):
            return

        if not self.__has_mod_permission(interaction):
            raise app_commands.MissingPermissions([])

        await interaction.response.defer()
        await self.prediction_manager.refresh_prediction_messages(interaction.guild_id)

        await self.bot.command_response(
            self.__cog_name__, interaction, "Successfully reloaded predictions."
        )

    @group.command(
        name="settings",
        description="Overview of all beans prediction related settings and their current value.",
    )
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def get_settings(self, interaction: discord.Interaction):
        output = self.settings_manager.get_settings_string(
            interaction.guild_id, SettingsManager.PREDICTIONS_SUBSETTINGS_KEY
        )
        await self.bot.command_response(self.__cog_name__, interaction, output)

    @group.command(
        name="toggle",
        description="Enable or disable the entire beans prediction module.",
    )
    @app_commands.describe(enabled="Turns the beans prediction module on or off.")
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def set_toggle(
        self, interaction: discord.Interaction, enabled: Literal["on", "off"]
    ):
        self.settings_manager.set_predictions_enabled(
            interaction.guild_id, enabled == "on"
        )
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"Beans prediction module was turned {enabled}.",
            args=[enabled],
        )

    @group.command(
        name="add_mod_role",
        description="Add prediction moderation privileges to a role.",
    )
    @app_commands.describe(role="This role will be allowed to moderate predictions.")
    @app_commands.check(__has_permission)
    async def add_mod_role(self, interaction: discord.Interaction, role: discord.Role):
        self.settings_manager.add_predictions_mod_role(interaction.guild_id, role.id)
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"Added {role.name} to prediction moderators.",
            args=[role.name],
        )

    @group.command(
        name="remove_mod_role",
        description="Remove prediction moderation privileges from a role.",
    )
    @app_commands.describe(role="Removes role from prediction moderators.")
    @app_commands.check(__has_permission)
    async def remove_mod_role(
        self, interaction: discord.Interaction, role: discord.Role
    ):
        self.settings_manager.remove_predictions_mod_role(interaction.guild_id, role.id)
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"Removed {role.name} from prediction moderators.",
            args=[role.name],
        )

    @group.command(
        name="add_predictions_channel",
        description="Add a channel where the prediction overview is gonna be displayed.",
    )
    @app_commands.describe(
        channel="This channel will be added to the predictions channels."
    )
    @app_commands.check(__has_permission)
    async def add_predictions_channel(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ):
        self.settings_manager.add_predictions_channel(interaction.guild_id, channel.id)
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"Added {channel.name} to prediction channels.",
            args=[channel.name],
        )

    @group.command(
        name="remove_predictions_channel",
        description="Add a channel where the prediction overview is gonna be displayed.",
    )
    @app_commands.describe(
        channel="This channel will be removed from the predictions channels."
    )
    @app_commands.check(__has_permission)
    async def remove_predictions_channel(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ):
        self.settings_manager.remove_predictions_channel(
            interaction.guild_id, channel.id
        )
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"Removed {channel.name} from prediction channels.",
            args=[channel.name],
        )


async def setup(bot):
    await bot.add_cog(Predictions(bot))
