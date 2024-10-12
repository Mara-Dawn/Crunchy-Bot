import asyncio
import datetime

import discord
from discord.ext import commands

from control.controller import Controller
from control.item_manager import ItemManager
from control.logger import BotLogger
from control.view.view_controller import ViewController
from datalayer.database import Database
from events.beans_event import BeansEvent
from events.bot_event import BotEvent
from events.inventory_event import InventoryEvent
from events.types import BeansEventType, EventType, UIEventType
from events.ui_event import UIEvent
from items.types import ItemGroup, ItemType
from view.combat.elements import MenuState
from view.shop.color_select_view import ShopColorSelectView  # noqa: F401
from view.shop.confirm_view import ShopConfirmView  # noqa: F401
from view.shop.prediction_submission_view import (
    ShopPredictionSubmissionView,  # noqa: F401
)
from view.shop.reaction_select_view import ShopReactionSelectView  # noqa: F401

# noqa: F401
from view.shop.response_view import ShopResponseView
from view.shop.user_select_view import ShopUserSelectView  # noqa: F401


class ShopInteraction:

    def __init__(
        self, interaction: discord.Interaction, selected: ItemType, view_id: int
    ):
        self.interaction = interaction
        self.selected = selected
        self.view_id = view_id


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
        self.shop_queue = asyncio.Queue()

        self.request_worker = asyncio.create_task(self.shop_request_worker())

    async def shop_request_worker(self):
        while True:
            request: ShopInteraction = await self.shop_queue.get()

            interaction = request.interaction
            selected = request.selected
            view_id = request.view_id

            if selected is None:
                await interaction.followup.send(
                    "Please select an Item first.", ephemeral=True
                )
                continue

            guild_id = interaction.guild_id
            member_id = interaction.user.id
            user_balance = await self.database.get_member_beans(guild_id, member_id)

            item = await self.item_manager.get_item(guild_id, selected)

            if user_balance < item.cost:
                await interaction.followup.send(
                    "You dont have enough beans to buy that.", ephemeral=True
                )
                continue

            inventory_items = await self.database.get_item_counts_by_user(
                guild_id, member_id
            )

            if item.max_amount is not None:
                item_count = 0

                if item.type in inventory_items:
                    item_count = inventory_items[item.type]

                if item_count >= item.max_amount:
                    await interaction.followup.send(
                        f"You cannot own more than {item.max_amount} items of this type.",
                        ephemeral=True,
                    )
                    continue

            # instantly used items and items with confirmation modals
            match item.group:
                case ItemGroup.IMMEDIATE_USE | ItemGroup.SUBSCRIPTION:
                    event = UIEvent(UIEventType.SHOP_DISABLE, True, view_id)
                    await self.controller.dispatch_ui_event(event)

                    embed = item.get_embed(self.bot, show_title=False, show_price=True)
                    view_class_name = item.view_class

                    view_class = globals()[view_class_name]
                    view: ShopResponseView = view_class(
                        self.controller, interaction, item, view_id
                    )

                    await view.init()

                    message = await interaction.followup.send(
                        "", embed=embed, view=view, ephemeral=True
                    )
                    view.set_message(message)
                    await view.refresh_ui()

                    continue

            event = BeansEvent(
                datetime.datetime.now(),
                guild_id,
                BeansEventType.SHOP_PURCHASE,
                member_id,
                -item.cost,
            )
            await self.controller.dispatch_event(event)

            # directly purchasable items without inventory
            match item.group:
                case ItemGroup.LOOTBOX:
                    await self.item_manager.drop_private_loot_box(
                        interaction,
                        size=item.base_amount,
                    )

                    continue

            # All other items get added to the inventory awaiting their trigger

            event = InventoryEvent(
                datetime.datetime.now(),
                guild_id,
                member_id,
                item.type,
                item.base_amount,
            )
            await self.controller.dispatch_event(event)

            log_message = f"{interaction.user.display_name} bought {item.name} for {item.cost} beans."
            self.logger.log(interaction.guild_id, log_message, cog="Shop")

            new_user_balance = await self.database.get_member_beans(guild_id, member_id)
            success_message = f"You successfully bought one **{item.name}** for `🅱️{item.cost}` beans. Remaining balance: `🅱️{new_user_balance}`\n Use */inventory* to check your inventory."

            await interaction.followup.send(success_message, ephemeral=True)

            self.shop_queue.task_done()

    async def listen_for_event(self, event: BotEvent) -> None:
        match event.type:
            case EventType.BEANS:
                beans_event: BeansEvent = event
                if beans_event.value == 0:
                    return
                new_user_balance = await self.database.get_member_beans(
                    beans_event.guild_id, beans_event.member_id
                )
                event = UIEvent(
                    UIEventType.SHOP_USER_REFRESH,
                    (beans_event.member_id, new_user_balance, None),
                )
                await self.controller.dispatch_ui_event(event)
            case EventType.INVENTORY:
                beans_event: InventoryEvent = event
                if beans_event.amount == 0:
                    return
                user_items = await self.database.get_item_counts_by_user(
                    beans_event.guild_id, beans_event.member_id
                )
                event = UIEvent(
                    UIEventType.SHOP_USER_REFRESH,
                    (beans_event.member_id, None, user_items),
                )
                await self.controller.dispatch_ui_event(event)

    async def listen_for_ui_event(self, event: UIEvent):
        match event.type:
            case UIEventType.SHOP_BUY:
                interaction = event.payload[0]
                selected_item = event.payload[1]

                shop_interaction = ShopInteraction(
                    interaction=interaction,
                    selected=selected_item,
                    view_id=event.view_id,
                )

                try:
                    exception = self.request_worker.exception()
                    if exception is not None:
                        raise exception
                        self.join_worker = asyncio.create_task(
                            self.shop_request_worker()
                        )
                except asyncio.CancelledError:
                    pass
                    self.request_worker = asyncio.create_task(
                        self.shop_request_worker()
                    )
                except asyncio.InvalidStateError:
                    pass

                await self.shop_queue.put(shop_interaction)

            case UIEventType.SHOP_CHANGED:
                guild_id = event.payload[0]
                member_id = event.payload[1]
                await self.refresh_ui(guild_id, member_id, event.view_id)
            case UIEventType.SHOW_INVENTORY:
                interaction = event.payload
                await self.send_inventory_message(interaction, event.view_id)

    async def refresh_ui(self, guild_id: int, member_id: int, view_id: int):
        new_user_balance = await self.database.get_member_beans(guild_id, member_id)
        user_items = await self.database.get_item_counts_by_user(guild_id, member_id)
        event = UIEvent(
            UIEventType.SHOP_REFRESH, (new_user_balance, user_items), view_id
        )
        await self.controller.dispatch_ui_event(event)

    async def send_inventory_message(
        self, interaction: discord.Interaction, view_id: int
    ):
        event = UIEvent(
            UIEventType.MAIN_MENU_STATE_CHANGE,
            (interaction, MenuState.INVENTORY, False),
            view_id,
        )
        await self.controller.dispatch_ui_event(event)
