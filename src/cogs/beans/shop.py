import datetime
import os
import traceback
from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands, tasks

from bot import CrunchyBot
from combat.types import UnlockableFeature
from config import Config
from control.combat.combat_embed_manager import CombatEmbedManager
from control.controller import Controller
from control.event_manager import EventManager
from control.interaction_manager import InteractionManager
from control.item_manager import ItemManager
from control.logger import BotLogger
from control.settings_manager import SettingsManager
from datalayer.database import Database
from datalayer.types import ItemTrigger
from error import ErrorHandler
from items.types import ItemType
from view.catalogue.embed import CatalogEmbed
from view.catalogue.view import CatalogView
from view.inventory.inventory_menu_view import InventoryMenuView
from view.shop.embed import ShopEmbed
from view.shop.view import ShopView


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
        self.item_handler: InteractionManager = self.controller.get_service(
            InteractionManager
        )
        self.embed_manager: CombatEmbedManager = self.controller.get_service(
            CombatEmbedManager
        )

    @staticmethod
    async def __has_permission(interaction: discord.Interaction) -> bool:
        author_id = int(os.environ.get(CrunchyBot.ADMIN_ID))
        return (
            interaction.user.id == author_id
            or interaction.user.guild_permissions.administrator
        )

    async def __beans_role_check(self, interaction: discord.Interaction) -> bool:
        member = interaction.user
        guild_id = interaction.guild_id

        beans_role = await self.settings_manager.get_beans_role(guild_id)
        if beans_role is None:
            return True
        if beans_role in [role.id for role in member.roles]:
            return True

        role_name = interaction.guild.get_role(beans_role).name
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"You can only use this command if you have the role `{role_name}`.",
        )
        return False

    async def __check_enabled(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id

        if not await self.settings_manager.get_shop_enabled(guild_id):
            await self.bot.command_response(
                self.__cog_name__,
                interaction,
                "Beans shop module is currently disabled.",
            )
            return False

        if (
            interaction.channel_id
            not in await self.settings_manager.get_beans_channels(guild_id)
        ):
            await self.bot.command_response(
                self.__cog_name__,
                interaction,
                "Shop commands cannot be used in this channel.",
            )
            return False

        stun_base_duration = (
            await self.item_manager.get_item(guild_id, ItemType.BAT)
        ).value
        stunned_remaining = await self.event_manager.get_stunned_remaining(
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

        try:
            for guild in self.bot.guilds:
                if not await self.settings_manager.get_beans_enabled(guild.id):
                    self.logger.log(
                        "sys", "Beans module disabled.", cog=self.__cog_name__
                    )
                    return

                await self.item_manager.consume_trigger_items(guild, ItemTrigger.DAILY)
        except Exception as e:
            print(traceback.format_exc())
            error_handler = ErrorHandler(self.bot)
            await error_handler.post_error(e)

    async def shop_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        items = [
            await self.item_manager.get_item(interaction.guild_id, enum)
            for enum in ItemType
        ]

        choices = [
            app_commands.Choice(
                name=item.name,
                value=item.type,
            )
            for item in items
            if current.lower() in item.name.lower()
        ][:25]
        return choices

    @app_commands.command(name="shop", description="Buy cool stuff with your beans.")
    @app_commands.guild_only()
    async def shop(self, interaction: discord.Interaction):
        if not await self.__check_enabled(interaction):
            return
        if not await self.__beans_role_check(interaction):
            return

        guild_level = await self.database.get_guild_level(interaction.guild_id)
        if guild_level < Config.UNLOCK_LEVELS[UnlockableFeature.SHOP]:
            await self.bot.command_response(
                self.__cog_name__,
                interaction,
                "Increase your server level to unlock this feature.",
            )
            return

        log_message = (
            f"{interaction.user.name} used command `{interaction.command.name}`."
        )
        self.logger.log(interaction.guild_id, log_message, cog=self.__cog_name__)
        await interaction.response.defer(ephemeral=True)

        shop_img = discord.File("./img/shop.png", "shop.png")
        items = await self.item_manager.get_shop_items(interaction.guild_id)

        items = sorted(items, key=lambda x: (x.shop_category.value, x.cost))

        user_balance = await self.database.get_member_beans(
            interaction.guild.id, interaction.user.id
        )
        user_items = await self.database.get_item_counts_by_user(
            interaction.guild.id, interaction.user.id
        )

        embed = ShopEmbed(self.bot, interaction.guild.name, items)
        view = ShopView(self.controller, interaction, items)

        message = await interaction.followup.send(
            "", embed=embed, view=view, files=[shop_img], ephemeral=True
        )
        view.set_message(message)
        await view.refresh_ui(user_balance=user_balance, user_items=user_items)

    @app_commands.command(
        name="catalog",
        description="A list of all items and where to get them.",
    )
    @app_commands.guild_only()
    async def catalog(self, interaction: discord.Interaction):
        if not await self.__check_enabled(interaction):
            return
        if not await self.__beans_role_check(interaction):
            return

        log_message = (
            f"{interaction.user.name} used command `{interaction.command.name}`."
        )
        self.logger.log(interaction.guild_id, log_message, cog=self.__cog_name__)
        await interaction.response.defer(ephemeral=True)

        guild_id = interaction.guild_id

        item_list = await self.item_manager.get_catalog_items(guild_id)
        embed = CatalogEmbed(self.bot)
        view = CatalogView(self.controller, interaction, item_list)

        message = await interaction.followup.send("", embed=embed, view=view)

        view.set_message(message)
        await view.refresh_ui()

    @app_commands.command(
        name="inventory",
        description="See the items you have bought from the beans shop.",
    )
    @app_commands.guild_only()
    async def inventory(self, interaction: discord.Interaction):
        if not await self.__check_enabled(interaction):
            return
        if not await self.__beans_role_check(interaction):
            return

        log_message = (
            f"{interaction.user.name} used command `{interaction.command.name}`."
        )
        self.logger.log(interaction.guild_id, log_message, cog=self.__cog_name__)
        await interaction.response.defer(ephemeral=True)

        member_id = interaction.user.id
        guild_id = interaction.guild_id

        inventory = await self.item_manager.get_user_inventory(guild_id, member_id)

        view = InventoryMenuView(self.controller, interaction, inventory)

        embeds = []
        loading_embed = discord.Embed(
            title="Loading Inventory", color=discord.Colour.light_grey()
        )
        self.embed_manager.add_text_bar(loading_embed, "", "Please Wait...")
        loading_embed.set_thumbnail(url=self.bot.user.display_avatar)
        embeds.append(loading_embed)

        message = await interaction.original_response()
        await message.edit(embeds=embeds, view=view, attachments=[])
        view.set_message(message)
        await view.refresh_ui()

    @app_commands.command(name="give_item", description="Modify user inventories.")
    @app_commands.describe(
        item="The item you want to give or take.",
        amount="The amount of items you want to give. Can be negative.",
        user="The user who shall recieve the item.",
    )
    @app_commands.check(__has_permission)
    @app_commands.autocomplete(item=shop_autocomplete)
    @app_commands.guild_only()
    async def give_item(
        self,
        interaction: discord.Interaction,
        item: str,
        amount: int,
        user: discord.Member,
    ):
        if item not in ItemType._value2member_map_:
            await self.bot.command_response(
                self.__cog_name__,
                interaction,
                "Item not found.",
                args=[item, amount],
            )
            return

        guild_id = interaction.guild_id
        member_id = user.id

        item_type = ItemType(item)
        item_obj = await self.item_manager.get_item(guild_id, item_type)

        await self.item_manager.give_item(
            guild_id, member_id, item_obj, amount, force=True
        )

        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"{amount}x {item_obj.name} was given to {user.display_name} by {interaction.user.display_name}.",
            args=[item, amount],
        )

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
        output = await self.settings_manager.get_settings_string(
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
        await self.settings_manager.set_shop_enabled(
            interaction.guild_id, enabled == "on"
        )
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"Beans shop module was turned {enabled}.",
            args=[enabled],
        )

    @group.command(
        name="price",
        description="Adjust item prices for the beans shop. Set to 0 to disable.",
    )
    @app_commands.describe(
        item="The item you are about to change.",
        amount="The new price for the specified item.",
    )
    @app_commands.check(__has_permission)
    @app_commands.autocomplete(item=shop_autocomplete)
    @app_commands.guild_only()
    async def price(
        self,
        interaction: discord.Interaction,
        item: str,
        amount: app_commands.Range[int, 0],
    ):
        if item not in ItemType._value2member_map_:
            await self.bot.command_response(
                self.__cog_name__,
                interaction,
                "Item not found.",
                args=[item, amount],
            )
            return

        item = ItemType(item)

        await self.settings_manager.set_shop_item_price(
            interaction.guild_id, item, amount
        )
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"Price for {item.value} was set to {amount} beans.",
            args=[item, amount],
        )


async def setup(bot):
    await bot.add_cog(Shop(bot))
