import datetime
import os
import random
import re
import time
from collections.abc import Callable
from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands, tasks

from bot import CrunchyBot
from control.ai_manager import AIManager
from control.controller import Controller
from control.event_manager import EventManager
from control.item_manager import ItemManager
from control.logger import BotLogger
from control.role_manager import RoleManager
from control.settings_manager import SettingsManager
from datalayer.database import Database
from events.inventory_batchevent import InventoryBatchEvent
from events.inventory_event import InventoryEvent
from events.karma_event import KarmaEvent
from items.types import ItemType
from view.settings.view import UserSettingView


class ColorInputModal(discord.ui.Modal):

    def __init__(self, callback: Callable, default_color: str):
        self.callback = callback
        super().__init__(title="Choose a Name Color")
        if default_color is not None:
            default_color = f"#{default_color}"
        self.hex_color = discord.ui.TextInput(
            label="Hex Color Code", placeholder="#FFFFFF", default=default_color
        )
        self.add_item(self.hex_color)

    # pylint: disable-next=arguments-differ
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        hex_string = self.hex_color.value
        match = re.search(r"^#(?:[0-9a-fA-F]{3}){1,2}$", hex_string)
        if not match:
            await interaction.followup.send(
                "Please enter a valid hex color value.", ephemeral=True
            )
            return

        await self.callback(interaction, hex_string.lstrip("#"))


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
        author_id = int(os.environ.get(CrunchyBot.ADMIN_ID))
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
        name="name_color",
        description="Set a custom name color for yourself.",
    )
    @app_commands.guild_only()
    async def name_color(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        member_id = interaction.user.id

        log_message = (
            f"{interaction.user.name} used command `{interaction.command.name}`."
        )
        self.logger.log(interaction.guild_id, log_message, cog=self.__cog_name__)

        if not await self.settings_manager.get_manual_name_color_enabled(guild_id):
            await interaction.response.send_message(
                "Manual name color selection is disabled.", ephemeral=True
            )
            return

        previous_color = await self.database.get_custom_color(guild_id, member_id)

        modal = ColorInputModal(
            self.apply_name_color,
            previous_color,
        )
        await interaction.response.send_modal(modal)

    async def apply_name_color(self, interaction: discord.Interaction, hex_color: str):
        await self.database.log_custom_color(
            interaction.guild_id, interaction.user.id, hex_color
        )
        await self.role_manager.update_username_color(
            interaction.guild_id, interaction.user.id
        )

    @app_commands.command(
        name="name_color_toggle",
        description="Enable or disable manually selecting name color.",
    )
    @app_commands.describe(enabled="Turns the name color selection on or off.")
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def name_color_toggle(
        self, interaction: discord.Interaction, enabled: Literal["on", "off"]
    ):
        await self.settings_manager.set_manual_name_color_enabled(
            interaction.guild_id, enabled == "on"
        )
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"Name Color selection was turned {enabled}.",
            args=[enabled],
        )

    @app_commands.command(
        name="personal_settings",
        description="Adjust various personal settings that only apply to you.",
    )
    @app_commands.guild_only()
    async def personal_settings(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        log_message = (
            f"{interaction.user.name} used command `{interaction.command.name}`."
        )
        self.logger.log(interaction.guild_id, log_message, cog=self.__cog_name__)

        view = UserSettingView(self.controller, interaction)
        message = await interaction.followup.send("", view=view, ephemeral=True)
        view.set_message(message)
        await view.refresh_ui()

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
        name="spam_inv_events",
        description="Increase the file size of your database with one simple trick!",
    )
    @app_commands.describe(
        loops="loops", amount="amount", batch="batch events, default True"
    )
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def spam_inv_events(
        self,
        interaction: discord.Interaction,
        loops: int,
        amount: int,
        batch: bool = True,
    ) -> None:
        await interaction.response.defer()
        t0 = time.time()
        guild_id = interaction.guild_id
        member_id = interaction.user.id
        for _loop in range(loops):
            itemtypes = list(ItemType)[:18]
            random_items = []

            for _number in range(amount):
                random_items.append((random.randrange(1, 10), random.choice(itemtypes)))

            if batch:
                event = InventoryBatchEvent(
                    datetime.datetime.now(),
                    guild_id,
                    member_id,
                    random_items,
                )

                await self.controller.dispatch_event(event)
            if not batch:
                for am, item in random_items:
                    event = InventoryEvent(
                        datetime.datetime.now(),
                        guild_id,
                        member_id,
                        item,
                        am,
                    )
                    await self.controller.dispatch_event(event)
        t1 = time.time()
        total_time = t1 - t0
        print(total_time)

        batchresponse = "batched " if batch else ""
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"{loops} loops of {amount} {batchresponse}inventory events created in {total_time} seconds",
        )


async def setup(bot):
    await bot.add_cog(Chat(bot))
