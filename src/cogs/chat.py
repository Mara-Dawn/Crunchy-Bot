import datetime
from typing import Literal

import discord
from bot import CrunchyBot
from control.ai_manager import AIManager
from control.controller import Controller
from control.event_manager import EventManager
from control.item_manager import ItemManager
from control.logger import BotLogger
from control.role_manager import RoleManager
from control.settings_manager import SettingsManager
from datalayer.database import Database
from discord import app_commands
from discord.ext import commands, tasks
from events.karma_event import KarmaEvent


class Chat(commands.Cog):

    def __init__(self, bot: CrunchyBot):
        self.bot = bot
        self.logger: BotLogger = bot.logger
        self.database: Database = bot.database
        self.controller: Controller = bot.controller
        self.item_manager: ItemManager = self.controller.get_service(ItemManager)
        self.event_manager: EventManager = self.controller.get_service(EventManager)
        self.role_manager: RoleManager = self.controller.get_service(RoleManager)
        self.settings_manager: SettingsManager = self.controller.get_service(
            SettingsManager
        )
        self.ai_manager: AIManager = self.controller.get_service(AIManager)

    @staticmethod
    async def __has_permission(interaction: discord.Interaction) -> bool:
        author_id = 90043934247501824
        return (
            interaction.user.id == author_id
            or interaction.user.guild_permissions.administrator
        )

    @commands.Cog.listener()
    async def on_ready(self):
        self.chat_timeout_check.start()
        self.logger.log(
            "init", str(self.__cog_name__) + " loaded.", cog=self.__cog_name__
        )

    @tasks.loop(minutes=10)
    async def chat_timeout_check(self):
        self.logger.debug(
            "sys", "ai chatlog decay check task started", cog=self.__cog_name__
        )
        count = self.ai_manager.clean_up_logs(1)

        if count > 0:
            self.logger.log(
                "sys", f"Cleaned up {count} old ai chat logs.", cog=self.__cog_name__
            )

    async def __karma_giving(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        positive: bool,
        yourself: str,
        too_soon: str,
        karma_amount: int,
        karma_message: str,
    ) -> None:
        if not await self.__check_enabled(interaction):
            return
        # await interaction.response.defer()

        if user is None:
            await self.bot.command_response(
                self.__cog_name__,
                interaction,
                "Missing user",
                args=[user.display_name],
                ephemeral=False,
            )
            return

        guild_id = interaction.guild_id
        recipient_id = user.id
        giver_id = interaction.user.id
        current_time = datetime.datetime.now()

        if recipient_id == giver_id:
            await self.bot.command_response(
                self.__cog_name__,
                interaction,
                yourself,
                args=[user.display_name],
                ephemeral=False,
            )
            return

        karma_events = await self.database.get_karma_events_by_giver_id(
            giver_id, guild_id, positive
        )

        if len(karma_events) > 0:

            current_date = datetime.datetime.now().date()
            last_karma_event_date = karma_events[0].datetime.date()

            if current_date == last_karma_event_date:
                await self.bot.command_response(
                    self.__cog_name__,
                    interaction,
                    too_soon + " tomorrow.",
                    args=[user.display_name],
                    ephemeral=False,
                )
                return

        # if len(karma_events) > 0:
        #     last_karma_event = karma_events[0]
        #     time_delta = current_time - last_karma_event.datetime
        #     karma_cd = int(
        #         int(datetime.datetime.now().timestamp())
        #         + await self.settings_manager.get_karma_cooldown(guild_id)
        #         - time_delta.total_seconds()
        #     )

        #     if (
        #         time_delta.total_seconds()
        #         <= await self.settings_manager.get_karma_cooldown(guild_id)
        #     ):
        #         await self.bot.command_response(
        #             self.__cog_name__,
        #             interaction,
        #             (too_soon + f" <t:{karma_cd}:R>."),
        #             args=[user.display_name],
        #             ephemeral=False,
        #         )
        #         return

        event = KarmaEvent(
            current_time,
            guild_id,
            karma_amount,
            recipient_id,
            giver_id,
        )

        await self.controller.dispatch_event(event)
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            karma_message,
            args=[user.display_name],
            ephemeral=False,
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id == self.bot.user.id:
            return

        if message.author.bot:
            return

        if not message.guild:
            return

        if not self.bot.user.mentioned_in(message):
            return

        beans_channels = await self.settings_manager.get_beans_channels(
            message.guild.id
        )
        jail_channels = await self.settings_manager.get_jail_channels(message.guild.id)
        if (
            message.channel.id not in beans_channels
            and message.channel.id not in jail_channels
        ):
            return

        await self.ai_manager.respond(message)

    async def __check_enabled(
        self,
        interaction: discord.Interaction,
    ):
        guild_id = interaction.guild_id

        if not await self.settings_manager.get_karma_enabled(guild_id):
            await self.bot.command_response(
                self.__cog_name__,
                interaction,
                "Karma module is currently disabled.",
            )
            return False

        return True

    @app_commands.command(name="give_karma", description="Give someone a gold star.")
    @app_commands.describe(user="Recipient of the gold star")
    @app_commands.guild_only()
    async def give_karma(
        self, interaction: discord.Interaction, user: discord.Member
    ) -> None:
        recipient_id = user.id
        giver_id = interaction.user.id
        await self.__karma_giving(
            interaction,
            user,
            True,
            "You can't give yourself karma, silly.",
            "Too soon, bozo.\nYou can give karma again",
            1,
            f"<@{giver_id}> gave <@{recipient_id}> a shiny gold star! 🌟",
        )

    @app_commands.command(name="fuck_you", description="Let someone know how you feel.")
    @app_commands.describe(user="Recipient of the fuck you")
    @app_commands.guild_only()
    async def fuck_you(
        self, interaction: discord.Interaction, user: discord.Member
    ) -> None:
        recipient_id = user.id
        giver_id = interaction.user.id
        await self.__karma_giving(
            interaction,
            user,
            False,
            "You can't fuck yourself, silly.",
            'Too soon, bozo.\nYou can say "fuck you" again',
            -1,
            f'<@{giver_id}> says "fuck you <@{recipient_id}>!" 🖕',
        )

    @app_commands.command(name="karma", description="How many gold stars do you have?")
    @app_commands.describe(user="How many gold stars do they have?")
    @app_commands.guild_only()
    async def karma(
        self,
        interaction: discord.Interaction,
        user: discord.Member | None = None,
    ) -> None:
        if not await self.__check_enabled(interaction):
            return
        await interaction.response.defer()

        if user is None:
            user = interaction.user

        guild_id = interaction.guild_id

        karma_events = await self.database.get_karma_events_by_recipient_id(
            user.id, guild_id
        )
        positive = 0
        negative = 0
        for event in karma_events:
            if event.amount > 0:
                positive += event.amount
            else:
                negative += event.amount

        star_stars = "star" if positive == 1 or positive == -1 else "stars"
        negative_plural = "" if negative == -1 or negative == 1 else "s"

        response = f'<@{user.id}> has accumulated {positive} gold {star_stars} 🌟 and {(abs(negative))} "fuck you"{negative_plural}! 🖕'
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            response,
            args=[user.display_name],
            ephemeral=False,
        )

    @app_commands.command(
        name="karma_settings",
        description="Overview of all karma related settings and their current value.",
    )
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def get_settings(self, interaction: discord.Interaction):
        output = await self.settings_manager.get_settings_string(
            interaction.guild_id, SettingsManager.KARMA_SUBSETTINGS_KEY
        )
        await self.bot.command_response(self.__cog_name__, interaction, output)

    @app_commands.command(
        name="karma_toggle",
        description="Enable or disable the entire karma module.",
    )
    @app_commands.describe(enabled="Turns the karma module on or off.")
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def set_toggle(
        self, interaction: discord.Interaction, enabled: Literal["on", "off"]
    ):
        await self.settings_manager.set_karma_enabled(
            interaction.guild_id, enabled == "on"
        )
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"Karma module was turned {enabled}.",
            args=[enabled],
        )

    @app_commands.command(
        name="set_karma_cooldown",
        description="Set the cooldown of the give_karma and fuck_you commands",
    )
    @app_commands.describe(
        cooldown="Cooldown in seconds, 1 day = 86400, 1 week = 604800"
    )
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def set_cooldown(
        self,
        interaction: discord.Interaction,
        cooldown: int,
    ):
        await self.settings_manager.set_karma_cooldown(interaction.guild_id, cooldown)
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"Karma cooldown was set to {cooldown} seconds",
            args=[cooldown],
        )


async def setup(bot):
    await bot.add_cog(Chat(bot))
