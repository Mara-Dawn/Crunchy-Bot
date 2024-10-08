import asyncio
import datetime
import os
import traceback
from typing import Literal  # noqa: UP035

import discord
from discord import ChannelType, app_commands
from discord.ext import commands

from bot import CrunchyBot
from control.controller import Controller
from control.event_manager import EventManager
from control.jail_manager import JailManager
from control.logger import BotLogger
from control.role_manager import RoleManager
from control.settings_manager import SettingsManager
from datalayer.database import Database
from datalayer.police_list import PoliceList
from events.jail_event import JailEvent
from events.spam_event import SpamEvent
from events.timeout_event import TimeoutEvent
from events.types import JailEventType
from view.settings_modal import SettingsModal


class Police(commands.Cog):

    def __init__(self, bot: CrunchyBot):
        self.bot = bot
        self.user_list: dict[int, PoliceList] = {}
        self.database: Database = bot.database
        self.logger: BotLogger = bot.logger
        self.controller: Controller = bot.controller
        self.event_manager: EventManager = self.controller.get_service(EventManager)
        self.role_manager: RoleManager = self.controller.get_service(RoleManager)
        self.jail_manager: JailManager = self.controller.get_service(JailManager)
        self.settings_manager: SettingsManager = self.controller.get_service(
            SettingsManager
        )

        self.initialized = False

    @staticmethod
    async def __has_permission(interaction: discord.Interaction) -> bool:
        author_id = int(os.environ.get(CrunchyBot.ADMIN_ID))
        return (
            interaction.user.id == author_id
            or interaction.user.guild_permissions.administrator
        )

    async def __jail_check(self, guild_id: int, user: discord.Member):
        if await self.settings_manager.get_jail_enabled(guild_id):
            return None

        timeout_count = await self.database.get_timeout_tracker_count(guild_id, user.id)
        timeout_count_threshold = (
            await self.settings_manager.get_police_timeouts_before_jail(guild_id)
        )

        if timeout_count >= timeout_count_threshold:
            self.logger.log(
                guild_id,
                f"Timeout jail threshold reached for {user.name}",
                cog=self.__cog_name__,
            )
            duration = await self.settings_manager.get_police_timeout_jail_duration(
                guild_id
            )
            success = await self.jail_manager.jail_user(
                guild_id, self.bot.user.id, user, duration
            )
            timestamp_now = int(datetime.datetime.now().timestamp())
            release = timestamp_now + (duration * 60)
            response = f"<@{user.id}> was timed out `{timeout_count}` times, resulting in a jail sentence."
            if success:
                await self.database.reset_timeout_tracker(guild_id, user.id)
                response += f" Their timeout count was reset and they will be released <t:{release}:R>."
            else:
                affected_jails = await self.database.get_active_jails_by_member(
                    guild_id, user.id
                )

                if len(affected_jails) <= 0:
                    self.logger.error(
                        guild_id,
                        "User already jailed but no active jail was found.",
                        cog=self.__cog_name__,
                    )
                    return None

                jail_id = affected_jails[0].id

                time_now = datetime.datetime.now()
                event = JailEvent(
                    time_now,
                    guild_id,
                    JailEventType.INCREASE,
                    self.bot.user.id,
                    duration,
                    jail_id,
                )
                await self.controller.dispatch_event(event)

                response += f" As they are already in jail, their sentence will be extended by `{duration}` minutes and their timeout count was reset."

            return response
        return None

    async def timeout_task(
        self, channel: discord.TextChannel, user: discord.Member, duration: int
    ):
        guild_id = channel.guild.id
        time_now = datetime.datetime.now()
        timestamp_now = int(time_now.timestamp())
        release = timestamp_now + duration

        naughty_list = self.user_list[guild_id]
        naughty_user = naughty_list.get_user(user.id)
        naughty_user.set_timeout_flag()

        event = TimeoutEvent(time_now, guild_id, user.id, duration)
        await self.controller.dispatch_event(event)

        try:
            timeout_role = await self.role_manager.get_timeout_role(channel.guild)
            await user.add_roles(timeout_role)

        except discord.Forbidden:
            self.logger.log(
                channel.guild.id,
                f"Missing permissions to change user roles of {user.name}.",
                cog=self.__cog_name__,
            )
            traceback.print_stack()
            traceback.print_exc()

        await channel.send(
            f"<@{user.id}> {await self.settings_manager.get_police_timeout_notice(guild_id)} Try again <t:{release}:R>.",
            delete_after=(duration),
        )
        self.logger.log(
            guild_id, f"Activated rate limit for {user.name}.", cog=self.__cog_name__
        )

        self.logger.log(
            channel.guild.id,
            f"Temporarily removed send_messages permission from {user.name}.",
            cog=self.__cog_name__,
        )

        timeout_length = duration - (
            int(datetime.datetime.now().timestamp()) - timestamp_now
        )

        await asyncio.sleep(timeout_length)

        naughty_user.release()
        self.logger.log(
            guild_id, f"User {user.name} rate limit was reset.", cog=self.__cog_name__
        )

        try:
            timeout_role = await self.role_manager.get_timeout_role(channel.guild)
            await user.remove_roles(timeout_role)

        except discord.Forbidden:
            self.logger.log(
                channel.guild.id,
                f"Missing permissions to change user roles of {user.name}.",
                cog=self.__cog_name__,
            )
            traceback.print_stack()
            traceback.print_exc()

        self.logger.log(
            guild_id,
            f"Reinstated old permissions for {user.name}.",
            cog=self.__cog_name__,
        )

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            self.user_list[guild.id] = PoliceList()

            timeout_role = await self.role_manager.get_timeout_role(guild)

            if len(timeout_role.members) > 0:
                self.logger.log(
                    "init",
                    "Ongoing timeouts found. Commencing cleanup.",
                    cog=self.__cog_name__,
                )

                for member in timeout_role.members:
                    await member.remove_roles(timeout_role)
                    self.logger.log(
                        "init",
                        f"Removed Timeout role from {member.display_name}.",
                        cog=self.__cog_name__,
                    )

        self.logger.log(
            "init", str(self.__cog_name__) + " loaded.", cog=self.__cog_name__
        )
        self.initialized = True

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        if not self.initialized:
            return
        self.user_list[guild.id] = PoliceList()

        await self.role_manager.reload_timeout_role(guild)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        if not self.initialized:
            return
        del self.user_list[guild.id]

    @commands.Cog.listener()
    async def on_message(self, message: discord.message.Message):
        if not self.initialized:
            return

        author_id = message.author.id
        if author_id == self.bot.user.id:
            return

        if message.author.bot:
            return

        if len(message.content) > 0 and message.content[0] == "/":
            return

        if not message.guild:
            return

        guild_id = message.guild.id

        if not await self.settings_manager.get_police_enabled(guild_id):
            return

        user_list = self.user_list[guild_id]

        message_limit = await self.settings_manager.get_police_message_limit(guild_id)
        message_limit_interval = (
            await self.settings_manager.get_police_message_limit_interval(guild_id)
        )

        if not user_list.has_user(author_id):
            self.logger.log(
                guild_id,
                f"Added rate tracking for user {message.author.name}",
                cog=self.__cog_name__,
            )
            user_list.add_user(author_id)

        user_node = user_list.get_user(author_id)

        user_list.track_spam_message(author_id, message.created_at)

        if user_node.spam_check(
            message_limit_interval, message_limit
        ) and user_node.check_spam_score_increase(
            message_limit_interval, message_limit
        ):
            event = SpamEvent(datetime.datetime.now(), guild_id, author_id)
            await self.controller.dispatch_event(event)

            self.logger.log(
                guild_id,
                f"Spam counter increased for {message.author.name}",
                cog=self.__cog_name__,
            )

        if bool(
            set([x.id for x in message.author.roles]).intersection(
                await self.settings_manager.get_police_naughty_roles(guild_id)
            )
        ):
            self.logger.debug(
                guild_id,
                f"{message.author.name} has matching roles",
                cog=self.__cog_name__,
            )

            if (
                user_node.is_in_timeout()
                or message.channel.id
                in await self.settings_manager.get_police_exclude_channels(guild_id)
                or message.channel.type == ChannelType.public_thread
                or message.channel.type == ChannelType.private_thread
            ):
                return

            user_list.track_timeout_message(author_id, message.created_at)

            if user_node.timeout_check(message_limit_interval, message_limit):
                await self.database.increment_timeout_tracker(guild_id, author_id)

                response = await self.__jail_check(guild_id, message.author)

                if response is not None:
                    await self.jail_manager.announce(message.guild, response)
                else:
                    duration = await self.settings_manager.get_police_timeout(guild_id)
                    self.bot.loop.create_task(
                        self.timeout_task(message.channel, message.author, duration)
                    )

        elif user_list.has_user(author_id):
            self.logger.log(
                guild_id,
                f"Removed rate tracking for user {message.author.name}",
                cog=self.__cog_name__,
            )
            user_list.remove_user(author_id)

    group = app_commands.Group(
        name="police", description="Subcommands for the Police module."
    )

    @app_commands.command(name="meow", description="Makes me meow!")
    async def meow(self, interaction: discord.Interaction) -> None:
        await self.bot.command_response(self.__cog_name__, interaction, "Meow!")

    @group.command(
        name="settings",
        description="Overview of all police related settings and their current value.",
    )
    @app_commands.check(__has_permission)
    async def get_settings(self, interaction: discord.Interaction):
        output = await self.settings_manager.get_settings_string(
            interaction.guild_id, SettingsManager.POLICE_SUBSETTINGS_KEY
        )
        await self.bot.command_response(self.__cog_name__, interaction, output)

    @app_commands.command(name="timeout", description="Timeout a user.")
    @app_commands.describe(
        user="User who will be timed out.",
        duration="Length of the timeout. (in seconds)",
    )
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def timeout(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        duration: app_commands.Range[int, 1],
    ):
        naughty_list = self.user_list[interaction.guild_id]

        if (
            naughty_list.has_user(user.id)
            and naughty_list.get_user(user.id).is_in_timeout()
        ):
            await self.bot.command_response(
                self.__cog_name__,
                interaction,
                "User already in timeout.",
                args=[user.name, duration],
            )

        if not naughty_list.has_user(user.id):
            message_limit = await self.settings_manager.get_police_message_limit(
                interaction.guild_id
            )
            self.logger.log(
                interaction.guild_id,
                f"Added rate tracking for user {user.name}",
                cog=self.__cog_name__,
            )
            naughty_list.add_user(user.id, message_limit)

        self.bot.loop.create_task(
            self.timeout_task(interaction.channel, user, duration)
        )
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            "User timed out successfully.",
            args=[user.name, duration],
        )

    @group.command(
        name="toggle", description="Enable or disable the entire police module."
    )
    @app_commands.describe(enabled="Turns the police module on or off.")
    @app_commands.check(__has_permission)
    async def set_toggle(
        self, interaction: discord.Interaction, enabled: Literal["on", "off"]
    ):
        await self.settings_manager.set_police_enabled(
            interaction.guild_id, enabled == "on"
        )
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"Police module was turned {enabled}.",
            args=[enabled],
        )

    @group.command(
        name="add_role", description="Add roles to be monitored by spam detection."
    )
    @app_commands.describe(role="The role that shall be tracked for spam detection.")
    @app_commands.check(__has_permission)
    async def add_role(self, interaction: discord.Interaction, role: discord.Role):
        await self.settings_manager.add_police_naughty_role(
            interaction.guild_id, role.id
        )
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"Added {role.name} to the list of active roles.",
            args=[role],
        )

    @group.command(name="remove_role", description="Remove roles from spam detection.")
    @app_commands.describe(role="Remove spam detection from this role.")
    @app_commands.check(__has_permission)
    async def remove_role(self, interaction: discord.Interaction, role: discord.Role):
        await self.settings_manager.remove_police_naughty_role(
            interaction.guild_id, role.id
        )
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"Removed {role.name} from active roles.",
            args=[role],
        )

    @group.command(
        name="untrack_channel", description="Stop tracking spam in specific channels."
    )
    @app_commands.describe(channel="Stop tracking spam for this channel.")
    @app_commands.check(__has_permission)
    async def untrack_channel(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ):
        await interaction.response.defer(ephemeral=True)
        await self.settings_manager.add_police_exclude_channel(
            interaction.guild_id, channel.id
        )
        await self.role_manager.reload_timeout_role(interaction.guild)
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"Stopping spam detection in {channel.name}.",
            args=[channel],
        )

    @group.command(
        name="track_channel",
        description="Reenable tracking spam for specific channels.",
    )
    @app_commands.describe(channel="Reenable tracking spam for this channel.")
    @app_commands.check(__has_permission)
    async def track_channel(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ):
        await interaction.response.defer(ephemeral=True)
        await self.settings_manager.remove_police_exclude_channel(
            interaction.guild_id, channel.id
        )
        await self.role_manager.reload_timeout_role(interaction.guild)
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"Resuming spam detection in {channel.name}.",
            args=[channel],
        )

    @group.command(
        name="setup", description="Opens a dialog to edit various police settings."
    )
    @app_commands.check(__has_permission)
    async def setup(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        modal = SettingsModal(
            self.bot,
            self.settings_manager,
            self.__cog_name__,
            interaction.command.name,
            "Settings for Police Features",
        )

        await modal.add_field(
            guild_id,
            SettingsManager.POLICE_SUBSETTINGS_KEY,
            SettingsManager.POLICE_TIMEOUT_LENGTH_KEY,
            int,
        )
        await modal.add_field(
            guild_id,
            SettingsManager.POLICE_SUBSETTINGS_KEY,
            SettingsManager.POLICE_MESSAGE_LIMIT_KEY,
            int,
        )
        await modal.add_field(
            guild_id,
            SettingsManager.POLICE_SUBSETTINGS_KEY,
            SettingsManager.POLICE_MESSAGE_LIMIT_INTERVAL_KEY,
            int,
        )
        await modal.add_field(
            guild_id,
            SettingsManager.POLICE_SUBSETTINGS_KEY,
            SettingsManager.POLICE_TIMEOUTS_BEFORE_JAIL_KEY,
            int,
        )
        await modal.add_field(
            guild_id,
            SettingsManager.POLICE_SUBSETTINGS_KEY,
            SettingsManager.POLICE_TIMEOUT_JAIL_DURATION_KEY,
            int,
        )

        await interaction.response.send_modal(modal)

    @group.command(name="set_timeout_message")
    @app_commands.describe(message="This will be sent to the timed out person.")
    @app_commands.check(__has_permission)
    async def set_message(self, interaction: discord.Interaction, message: str):

        await self.settings_manager.set_police_timeout_notice(
            interaction.guild_id, message
        )
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"Timeout warning set to:\n `{message}`",
            args=[message],
        )


async def setup(bot):
    await bot.add_cog(Police(bot))
