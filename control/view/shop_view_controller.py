import datetime

import discord
from discord.ext import commands

from control.controller import Controller
from control.item_manager import ItemManager
from control.logger import BotLogger
from control.view.view_controller import ViewController
from datalayer.database import Database
from events.beans_event import BeansEvent
from events.inventory_event import InventoryEvent
from events.lootbox_event import LootBoxEvent
from events.types import BeansEventType, LootBoxEventType, UIEventType
from events.ui_event import UIEvent
from items.types import ItemGroup, ItemType
from view.inventory_embed import InventoryEmbed
from view.lootbox_view import LootBoxView
from view.shop_color_select_view import ShopColorSelectView  # noqa: F401
from view.shop_confirm_view import ShopConfirmView  # noqa: F401
from view.shop_reaction_select_view import ShopReactionSelectView  # noqa: F401
from view.shop_response_view import ShopResponseView
from view.shop_user_select_view import ShopUserSelectView  # noqa: F401


class ShopViewController(ViewController):

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
        self.item_manager: ItemManager = controller.get_service(ItemManager)

    async def listen_for_ui_event(self, event: UIEvent):
        match event.get_type():
            case UIEventType.SHOP_BUY:
                interaction = event.get_payload()[0]
                selected_item = event.get_payload()[1]
                self.buy(interaction, selected_item, event.get_view_id())
            case UIEventType.SHOP_CHANGED:
                guild_id = event.get_payload()[0]
                member_id = event.get_payload()[1]
                self.refresh_ui(guild_id, member_id, event.get_view_id())
            case UIEventType.SHOW_INVENTORY:
                interaction = event.get_payload()
                self.send_inventory_message()(interaction)

    async def refresh_ui(self, guild_id: int, member_id: int, view_id: int):
        new_user_balance = self.database.get_member_beans(guild_id, member_id)
        event = UIEvent(UIEventType.SHOP_REFRESH, new_user_balance, view_id)
        await self.controller.dispatch_ui_event(event)

    async def buy(
        self, interaction: discord.Interaction, selected: ItemType, view_id: int
    ):

        if selected is None:
            await interaction.response.send_message(
                "Please select an Item first.", ephemeral=True
            )
            return

        guild_id = interaction.guild_id
        member_id = interaction.user.id
        user_balance = self.database.get_member_beans(guild_id, member_id)

        item = self.item_manager.get_item(guild_id, selected)

        if user_balance < item.get_cost():
            await interaction.response.send_message(
                "You dont have enough beans to buy that.", ephemeral=True
            )
            return

        inventory_items = self.database.get_item_counts_by_user(guild_id, member_id)

        if item.get_max_amount() is not None:
            item_count = 0

            if item.get_type() in inventory_items:
                item_count = inventory_items[item.get_type()]

            if item_count >= item.get_max_amount():
                await interaction.response.send_message(
                    f"You cannot own more than {item.get_max_amount()} items of this type.",
                    ephemeral=True,
                )
                return

        # instantly used items and items with confirmation modals
        match item.get_group():
            case ItemGroup.IMMEDIATE_USE | ItemGroup.SUBSCRIPTION:
                await interaction.response.defer(ephemeral=True)

                embed = item.get_embed()
                view_class_name = item.get_view_class()

                view_class = globals()[view_class_name]
                view: ShopResponseView = view_class(self.controller, interaction, item)

                message = await interaction.followup.send(
                    "", embed=embed, view=view, ephemeral=True
                )
                await view.set_message(message)

                event = UIEvent(UIEventType.SHOP_DISABLE, True, view_id)
                await self.controller.dispatch_ui_event(event)

                return

        event = BeansEvent(
            datetime.datetime.now(),
            guild_id,
            BeansEventType.SHOP_PURCHASE,
            member_id,
            -item.get_cost(),
        )
        await self.controller.dispatch_event(event)

        # directly purchasable items without inventory
        match item.get_group():
            case ItemGroup.LOOTBOX:
                await interaction.response.defer()

                loot_box = self.item_manager.create_loot_box(guild_id)

                title = f"{interaction.user.display_name}'s Random Treasure Chest"
                description = f"Only you can claim this, <@{interaction.user.id}>!"
                embed = discord.Embed(
                    title=title, description=description, color=discord.Colour.purple()
                )
                embed.set_image(url="attachment://treasure_closed.png")

                item = None
                if loot_box.get_item_type() is not None:
                    item = self.item_manager.get_item(
                        guild_id, loot_box.get_item_type()
                    )

                view = LootBoxView(self.controller, owner_id=interaction.user.id)

                treasure_close_img = discord.File(
                    "./img/treasure_closed.png", "treasure_closed.png"
                )

                message = await interaction.followup.send(
                    "", embed=embed, view=view, files=[treasure_close_img]
                )
                new_user_balance = self.database.get_member_beans(guild_id, member_id)

                event = UIEvent(UIEventType.SHOP_REFRESH, new_user_balance)
                await self.controller.dispatch_ui_event(event)

                loot_box.set_message_id(message.id)
                loot_box_id = self.database.log_lootbox(loot_box)

                event = LootBoxEvent(
                    datetime.datetime.now(),
                    guild_id,
                    loot_box_id,
                    interaction.user.id,
                    LootBoxEventType.BUY,
                )
                await self.controller.dispatch_event(event)
                return

        # All other items get added to the inventory awaiting their trigger

        event = InventoryEvent(
            datetime.datetime.now(),
            guild_id,
            member_id,
            item.get_type(),
            item.get_base_amount(),
        )
        await self.controller.dispatch_event(event)

        log_message = f"{interaction.user.display_name} bought {item.get_name()} for {item.get_cost()} beans."
        self.logger.log(interaction.guild_id, log_message, cog="Shop")

        new_user_balance = self.database.get_member_beans(guild_id, member_id)
        success_message = f"You successfully bought one **{item.get_name()}** for `🅱️{item.get_cost()}` beans. Remaining balance: `🅱️{new_user_balance}`\n Use */inventory* to check your inventory."

        await interaction.response.send_message(success_message, ephemeral=True)

        event = UIEvent(UIEventType.SHOP_REFRESH, new_user_balance, view_id)
        await self.controller.dispatch_ui_event(event)

    async def send_inventory_message(self, interaction: discord.Interaction):
        inventory = self.item_manager.get_user_inventory(
            interaction.guild_id, interaction.user.id
        )

        police_img = discord.File("./img/police.png", "police.png")

        embed = InventoryEmbed(inventory)

        await interaction.followup.send(
            "", embed=embed, files=[police_img], ephemeral=True
        )

        return
