import datetime
import discord
from control.view import (
    LootBoxViewController,
    ShopResponseViewController,
    ViewController,
)
from events import BeansEvent, BotEvent, InventoryEvent, LootBoxEvent, UIEvent
from events.types import BeansEventType, LootBoxEventType, UIEventType
from items.types import ItemGroup, ItemType
from view import InventoryEmbed, LootBoxView, ShopResponseView

# needed for global access
# pylint: disable=unused-import
from view import (
    ShopUserSelectView,
    ShopConfirmView,
    ShopColorSelectView,
    ShopReactionSelectView,
)

# pylint: enable=unused-import


class ShopViewController(ViewController):

    async def listen_for_event(self, event: BotEvent):
        pass

    async def refresh_ui(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        member_id = interaction.user.id
        new_user_balance = self.database.get_member_beans(guild_id, member_id)
        event = UIEvent(guild_id, member_id, UIEventType.REFRESH_SHOP, new_user_balance)
        await self.controller.dispatch_ui_event(event)

    async def buy(self, interaction: discord.Interaction, selected: ItemType):

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

            if item.get_type() in inventory_items.keys():
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
                view_controller = self.controller.get_view_controller(
                    ShopResponseViewController
                )
                view: ShopResponseView = view_class(view_controller, interaction, item)

                message = await interaction.followup.send(
                    "", embed=embed, view=view, ephemeral=True
                )
                await view.set_message(message)

                event = UIEvent(guild_id, member_id, UIEventType.DISABLE_SHOP, True)
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
                embed.set_image(url="attachment://treasure_closed.jpg")

                item = None
                if loot_box.get_item_type() is not None:
                    item = self.item_manager.get_item(
                        guild_id, loot_box.get_item_type()
                    )

                view_controller = self.controller.get_view_controller(
                    LootBoxViewController
                )
                view = LootBoxView(view_controller, owner_id=interaction.user.id)

                treasure_close_img = discord.File(
                    "./img/treasure_closed.jpg", "treasure_closed.jpg"
                )

                message = await interaction.followup.send(
                    "", embed=embed, view=view, files=[treasure_close_img]
                )
                new_user_balance = self.database.get_member_beans(guild_id, member_id)

                event = UIEvent(
                    guild_id, member_id, UIEventType.REFRESH_SHOP, new_user_balance
                )
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

        event = UIEvent(guild_id, member_id, UIEventType.REFRESH_SHOP, new_user_balance)
        await self.controller.dispatch_ui_event(event)

    def get_inventory_embed(self, interaction: discord.Interaction):
        inventory = self.item_manager.get_user_inventory(
            interaction.guild_id, interaction.user.id
        )
        return InventoryEmbed(inventory)
