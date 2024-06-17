import datetime

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

    KARMA_TIME_THRESHOLD = 60 * 60 * 24 * 7

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

    @app_commands.command(name="give_karma", description="Give someone a gold star.")
    @app_commands.describe(user="Recipient of the gold star")
    @app_commands.guild_only()
    async def balance(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
    ) -> None:
        # if not await self.__check_enabled(interaction):
        #     return
        await interaction.response.defer()

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

        karma_events = await self.database.get_karma_events_by_giver_id(
            giver_id, guild_id
        )
        if len(karma_events) > 0:
            last_karma_event = karma_events[0]
            time_delta = current_time - last_karma_event.datetime
            if time_delta.total_seconds() <= self.KARMA_TIME_THRESHOLD:
                await self.bot.command_response(
                    self.__cog_name__,
                    interaction,
                    "Too soon, bozo",
                    args=[user.display_name],
                    ephemeral=False,
                )
                return

        event = KarmaEvent(
            current_time,
            guild_id,
            1,
            recipient_id,
            giver_id,
        )

        await self.controller.dispatch_event(event)
        response = f"<@{giver_id}> gave <@{recipient_id}> a shiny gold star!"
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            response,
            args=[user.display_name],
            ephemeral=False,
        )

    @app_commands.command(name="karma", description="How many gold stars do you have?")
    @app_commands.describe(user="How many gold stars do they have?")
    @app_commands.guild_only()
    async def karma(
        self,
        interaction: discord.Interaction,
        user: discord.Member | None = None,
    ) -> None:
        # if not await self.__check_enabled(interaction):
        #     return
        await interaction.response.defer()

        if user is None:
            user = interaction.user

        guild_id = interaction.guild_id

        karma_events = await self.database.get_karma_events_by_recipient_id(
            user.id, guild_id
        )
        num = 0
        for event in karma_events:
            num += event.amount

        response = f"<@{user.id}> has accumulated {num} gold stars!"
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            response,
            args=[user.display_name],
            ephemeral=False,
        )


async def setup(bot):
    await bot.add_cog(Chat(bot))
