import datetime
from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands, tasks

from bot import CrunchyBot
from control.controller import Controller
from control.event_manager import EventManager
from control.item_manager import ItemManager
from control.logger import BotLogger
from control.settings_manager import SettingsManager
from datalayer.database import Database
from datalayer.types import ItemTrigger
from items.types import ItemType
from view.inventory_embed import InventoryEmbed
from view.shop_embed import ShopEmbed
from view.shop_view import ShopView


class Shop(commands.Cog):

    def __init__(self, bot: CrunchyBot):
        self.bot = bot
        self.logger: BotLogger = bot.logger
        self.database: Database = bot.database
        self.controller: Controller = bot.controller
        self.item_manager: ItemManager = self.controller.get_service(ItemManager)
        self.event_manager: EventManager = self.controller.get_service(EventManager)
        self.settings_manager: SettingsManager = self.controller.get_service(
            SettingsManager
        )

    @staticmethod
    async def __has_permission(interaction: discord.Interaction) -> bool:
        author_id = 90043934247501824
        return (
            interaction.user.id == author_id
            or interaction.user.guild_permissions.administrator
        )

    async def __check_enabled(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id

        if not self.settings_manager.get_shop_enabled(guild_id):
            await self.bot.command_response(
                self.__cog_name__,
                interaction,
                "Beans shop module is currently disabled.",
            )
            return False

        if interaction.channel_id not in self.settings_manager.get_beans_channels(
            guild_id
        ):
            await self.bot.command_response(
                self.__cog_name__,
                interaction,
                "Shop commands cannot be used in this channel.",
            )
            return False

        stun_base_duration = self.item_manager.get_item(guild_id, ItemType.BAT).value
        stunned_remaining = self.event_manager.get_stunned_remaining(
            guild_id, interaction.user.id, stun_base_duration
        )

        if stunned_remaining > 0:
            timestamp_now = int(datetime.datetime.now().timestamp())
            remaining = int(timestamp_now + stunned_remaining)
            await self.bot.command_response(
                self.__cog_name__,
                interaction,
                f"You are currently stunned from a bat attack. Try again <t:{remaining}:R>",
            )
            return False

        return True

    @commands.Cog.listener()
    async def on_ready(self):
        self.daily_collection_task.start()
        self.logger.log(
            "init", str(self.__cog_name__) + " loaded.", cog=self.__cog_name__
        )

    @tasks.loop(time=datetime.time(hour=0))
    async def daily_collection_task(self):
        self.logger.log("sys", "Daily Item Check started.", cog=self.__cog_name__)

        for guild in self.bot.guilds:
            if not self.settings_manager.get_beans_enabled(guild.id):
                self.logger.log("sys", "Beans module disabled.", cog=self.__cog_name__)
                return

            await self.item_manager.use_items(guild.id, ItemTrigger.DAILY)

    @app_commands.command(name="shop", description="Buy cool stuff with your beans.")
    @app_commands.guild_only()
    async def shop(self, interaction: discord.Interaction):
        if not await self.__check_enabled(interaction):
            return

        log_message = (
            f"{interaction.user.name} used command `{interaction.command.name}`."
        )
        self.logger.log(interaction.guild_id, log_message, cog=self.__cog_name__)
        await interaction.response.defer(ephemeral=True)

        shop_img = discord.File("./img/shop.png", "shop.png")
        police_img = discord.File("./img/police.png", "police.png")
        items = self.item_manager.get_items(interaction.guild_id)

        items = sorted(items, key=lambda x: (x.shop_category.value, x.cost))

        user_balance = self.database.get_member_beans(
            interaction.guild.id, interaction.user.id
        )
        user_items = self.database.get_item_counts_by_user(
            interaction.guild.id, interaction.user.id
        )
        embed = ShopEmbed(interaction.guild.name, interaction.user.id, items)

        view = ShopView(self.controller, interaction, items)

        message = await interaction.followup.send(
            "", embed=embed, view=view, files=[shop_img, police_img], ephemeral=True
        )
        view.set_message(message)
        await view.refresh_ui(user_balance=user_balance, user_items=user_items)

    @app_commands.command(
        name="inventory",
        description="See the items you have bought from the beans shop.",
    )
    @app_commands.guild_only()
    async def inventory(self, interaction: discord.Interaction):
        if not await self.__check_enabled(interaction):
            return

        log_message = (
            f"{interaction.user.name} used command `{interaction.command.name}`."
        )
        self.logger.log(interaction.guild_id, log_message, cog=self.__cog_name__)
        await interaction.response.defer(ephemeral=True)

        police_img = discord.File("./img/police.png", "police.png")

        member_id = interaction.user.id
        guild_id = interaction.guild_id

        inventory = self.item_manager.get_user_inventory(guild_id, member_id)
        embed = InventoryEmbed(inventory)

        await interaction.followup.send("", embed=embed, files=[police_img])

    group = app_commands.Group(
        name="beansshop", description="Subcommands for the Beans Shop module."
    )

    @group.command(
        name="settings",
        description="Overview of all beans shop related settings and their current value.",
    )
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def get_settings(self, interaction: discord.Interaction):
        output = self.settings_manager.get_settings_string(
            interaction.guild_id, SettingsManager.SHOP_SUBSETTINGS_KEY
        )
        await self.bot.command_response(self.__cog_name__, interaction, output)

    @group.command(
        name="toggle", description="Enable or disable the entire beans shop module."
    )
    @app_commands.describe(enabled="Turns the beans shop module on or off.")
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def set_toggle(
        self, interaction: discord.Interaction, enabled: Literal["on", "off"]
    ):
        self.settings_manager.set_shop_enabled(interaction.guild_id, enabled == "on")
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"Beans shop module was turned {enabled}.",
            args=[enabled],
        )

    @group.command(name="price", description="Adjust item prices for the beans shop.")
    @app_commands.describe(
        item="The item you are about to change.",
        amount="The new price for the specified item.",
    )
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def price(
        self,
        interaction: discord.Interaction,
        item: ItemType,
        amount: app_commands.Range[int, 1],
    ):
        self.settings_manager.set_shop_item_price(
            interaction.guild_id, item.value, amount
        )
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"Price for {item.value} was set to {amount} beans.",
            args=[item, amount],
        )


async def setup(bot):
    await bot.add_cog(Shop(bot))
