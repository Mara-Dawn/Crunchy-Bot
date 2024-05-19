import datetime
import secrets

import discord
from datalayer.database import Database
from datalayer.inventory import UserInventory
from discord.ext import commands
from events.beans_event import BeansEvent
from events.bot_event import BotEvent
from events.inventory_event import InventoryEvent
from events.types import BeansEventType, EventType, UIEventType
from events.ui_event import UIEvent
from items import Debuff
from items.item import Item
from items.types import ItemState, ItemType
from view.types import ActionType

from control.controller import Controller
from control.item_manager import ItemManager
from control.logger import BotLogger
from control.view.view_controller import ViewController


class InventoryViewController(ViewController):

    def __init__(
        self,
        bot: commands.Bot,
        logger: BotLogger,
        database: Database,
        controller: Controller,
    ):
        super().__init__(bot, logger, database)
        self.controller = controller
        self.item_manager: ItemManager = controller.get_service(ItemManager)

    async def listen_for_event(self, event: BotEvent) -> None:
        member_id = None
        guild_id = None
        match event.type:
            case EventType.BEANS:
                event: BeansEvent = event
                guild_id = event.guild_id
                member_id = event.member_id
            case EventType.INVENTORY:
                event: InventoryEvent = event
                guild_id = event.guild_id
                member_id = event.member_id

        if member_id is not None and guild_id is not None:
            inventory = await self.item_manager.get_user_inventory(guild_id, member_id)
            event = UIEvent(UIEventType.INVENTORY_USER_REFRESH, inventory)
            await self.controller.dispatch_ui_event(event)

    async def listen_for_ui_event(self, event: UIEvent):
        match event.type:
            case UIEventType.INVENTORY_ITEM_ACTION:
                interaction = event.payload[0]
                item_type = event.payload[1]
                item_action = event.payload[2]
                await self.item_action(
                    interaction, item_type, item_action, event.view_id
                )
            case UIEventType.INVENTORY_SELL:
                interaction = event.payload[0]
                item_type = event.payload[1]
                amount = event.payload[2]
                sell_until = event.payload[3]
                await self.sell(
                    interaction, item_type, amount, sell_until, event.view_id
                )
            case UIEventType.SHOP_RESPONSE_USER_SUBMIT:
                if event.view_id is not None:
                    return
                interaction = event.payload[0]
                shop_data = event.payload[1]
                selected_user = shop_data.selected_user
                item = shop_data.item
                await self.submit_user_view(interaction, selected_user, item)

    async def sell(
        self,
        interaction: discord.Interaction,
        item_type: ItemType,
        amount: int,
        sell_until: bool,
        view_id: int,
    ):
        guild_id = interaction.guild_id
        user_id = interaction.user.id
        inventory = await self.item_manager.get_user_inventory(guild_id, user_id)

        item_owned = inventory.get_item_count(item_type)

        if not sell_until and item_owned < amount:
            await interaction.followup.send(
                "You dont have this many items to sell.",
                ephemeral=True,
            )
            return

        sell_amount = amount

        if sell_until:
            sell_amount = max(0, item_owned - amount)

        if sell_amount == 0:
            return

        event = InventoryEvent(
            datetime.datetime.now(),
            guild_id,
            user_id,
            item_type,
            -sell_amount,
        )
        await self.controller.dispatch_event(event)

        item = await self.item_manager.get_item(guild_id, item_type)

        beans = sell_amount * int(
            min((item.cost * UserInventory.SELL_MODIFIER) / item.base_amount, 100)
        )
        event = BeansEvent(
            datetime.datetime.now(),
            guild_id,
            BeansEventType.SHOP_BUYBACK,
            user_id,
            beans,
        )
        await self.controller.dispatch_event(event)

    async def submit_user_view(
        self,
        interaction: discord.Interaction,
        target: discord.Member,
        item: Item,
    ):
        guild_id = interaction.guild_id
        user_id = interaction.user.id

        match item.type:
            case ItemType.SPOOK_BEAN:
                if target is not None and target.bot:
                    await interaction.followup.send(
                        "You cannot select bot users.", ephemeral=True
                    )
                    return

                if target is None:
                    await interaction.followup.send(
                        "Please select a user first.", ephemeral=True
                    )
                    return

                ghost = secrets.choice(Debuff.DEBUFFS)

                event = InventoryEvent(
                    datetime.datetime.now(),
                    guild_id,
                    target.id,
                    ghost,
                    Debuff.DEBUFF_DURATION,
                )
                await self.controller.dispatch_event(event)
                event = InventoryEvent(
                    datetime.datetime.now(),
                    guild_id,
                    user_id,
                    item.type,
                    -1,
                )
                await self.controller.dispatch_event(event)

                await interaction.followup.send(
                    f"{target.display_name} was possessed by a random ghost.",
                    ephemeral=True,
                )
                message = await interaction.original_response()
                await message.delete()

    async def item_action(
        self,
        interaction: discord.Interaction,
        item_type: ItemType,
        item_action: ActionType,
        view_id: int,
    ):
        guild_id = interaction.guild_id
        user_id = interaction.user.id
        item_state = ItemState.ENABLED

        match item_action:
            case ActionType.DISABLE_ACTION:
                item_state = ItemState.DISABLED
                await self.database.log_item_state(
                    guild_id, user_id, item_type, item_state
                )
            case ActionType.ENABLE_ACTION:
                item_state = ItemState.ENABLED
                await self.database.log_item_state(
                    guild_id, user_id, item_type, item_state
                )
            case ActionType.USE_ACTION:
                await self.item_manager.use_item_interaction(interaction, item_type)

        inventory = await self.item_manager.get_user_inventory(guild_id, user_id)

        event = UIEvent(UIEventType.INVENTORY_REFRESH, inventory, view_id)
        await self.controller.dispatch_ui_event(event)
