import asyncio
import datetime
import secrets

import discord
from discord.ext import commands

from combat.enemies.types import EnemyType
from control.combat.encounter_manager import EncounterManager
from control.controller import Controller
from control.item_manager import ItemManager
from control.logger import BotLogger
from control.settings_manager import SettingsManager
from control.view.view_controller import ViewController
from datalayer.database import Database
from datalayer.inventory import UserInventory
from events.beans_event import BeansEvent
from events.bot_event import BotEvent
from events.inventory_event import InventoryEvent
from events.types import BeansEventType, EventType, UIEventType
from events.ui_event import UIEvent
from items import BaseKey, Debuff
from items.item import Item
from items.types import ItemState, ItemType
from view.shop.embed import ShopEmbed
from view.shop.view import ShopView
from view.types import ActionType


class InventoryInteraction:
    def __init__(
        self,
        interaction: discord.Interaction,
        event_type: UIEventType,
        view_id: int,
    ):
        self.interaction = interaction
        self.event_type = event_type
        self.view_id = view_id


class InventoryItemAction(InventoryInteraction):
    def __init__(
        self,
        interaction: discord.Interaction,
        item_type: ItemType,
        item_action: ActionType,
        view_id: int,
    ):
        super().__init__(
            interaction=interaction,
            event_type=UIEventType.INVENTORY_ITEM_ACTION,
            view_id=view_id,
        )
        self.item_type = item_type
        self.item_action = item_action


class InventorySellAction(InventoryInteraction):
    def __init__(
        self,
        interaction: discord.Interaction,
        item_type: ItemType,
        amount: int,
        sell_until: bool,
        view_id: int,
    ):
        super().__init__(
            interaction=interaction,
            event_type=UIEventType.INVENTORY_SELL,
            view_id=view_id,
        )
        self.item_type = item_type
        self.amount = amount
        self.sell_until = sell_until


class InventoryCombineAction(InventoryInteraction):
    def __init__(
        self,
        interaction: discord.Interaction,
        item_type: ItemType,
        amount: int,
        combine_until: bool,
        view_id: int,
    ):
        super().__init__(
            interaction=interaction,
            event_type=UIEventType.INVENTORY_COMBINE,
            view_id=view_id,
        )
        self.item_type = item_type
        self.amount = amount
        self.combine_until = combine_until


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
        self.encounter_manager: EncounterManager = self.controller.get_service(
            EncounterManager
        )
        self.settings_manager: SettingsManager = self.controller.get_service(
            SettingsManager
        )

        self.request_queue = asyncio.Queue()
        self.request_worker = asyncio.create_task(self.inventory_worker())

    async def inventory_worker(self):
        while True:
            request: InventoryInteraction = await self.request_queue.get()

            match request.event_type:
                case UIEventType.INVENTORY_ITEM_ACTION:
                    action_request: InventoryItemAction = request
                    await self.item_action(action_request)
                case UIEventType.INVENTORY_SELL:
                    sell_request: InventorySellAction = request
                    await self.sell(sell_request)
                case UIEventType.INVENTORY_COMBINE:
                    combine_request: InventoryCombineAction = request
                    await self.combine(combine_request)

            self.request_queue.task_done()

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

                request = InventoryItemAction(
                    interaction=interaction,
                    item_type=item_type,
                    item_action=item_action,
                    view_id=event.view_id,
                )
                await self.request_queue.put(request)

            case UIEventType.INVENTORY_SELL:
                interaction = event.payload[0]
                item_type = event.payload[1]
                amount = event.payload[2]
                sell_until = event.payload[3]

                request = InventorySellAction(
                    interaction=interaction,
                    item_type=item_type,
                    amount=amount,
                    sell_until=sell_until,
                    view_id=event.view_id,
                )
                await self.request_queue.put(request)

            case UIEventType.INVENTORY_COMBINE:
                interaction = event.payload[0]
                item_type = event.payload[1]
                amount = event.payload[2]
                combine_until = event.payload[3]

                request = InventoryCombineAction(
                    interaction=interaction,
                    item_type=item_type,
                    amount=amount,
                    combine_until=combine_until,
                    view_id=event.view_id,
                )
                await self.request_queue.put(request)

            case UIEventType.INVENTORY_RESPONSE_CONFIRM_SUBMIT:
                interaction = event.payload[0]
                item = event.payload[1]
                await self.submit_confirm_view(interaction, item, event.view_id)

            case UIEventType.SHOP_RESPONSE_USER_SUBMIT:
                if event.view_id is not None:
                    return
                interaction = event.payload[0]
                shop_data = event.payload[1]
                selected_user = shop_data.selected_user
                item = shop_data.item
                await self.submit_user_view(
                    interaction, selected_user, item, event.view_id
                )
            case UIEventType.SHOW_SHOP:
                interaction = event.payload
                await self.open_shop(interaction, event.view_id)

    async def sell(
        self,
        request: InventorySellAction,
    ):
        interaction = request.interaction
        item_type = request.item_type
        amount = request.amount
        sell_until = request.sell_until

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

    async def combine(
        self,
        request: InventoryCombineAction,
    ):
        interaction = request.interaction
        item_type = request.item_type
        amount = request.amount
        combine_until = request.combine_until

        guild_id = interaction.guild_id
        user_id = interaction.user.id
        inventory = await self.item_manager.get_user_inventory(guild_id, user_id)

        item_owned = inventory.get_item_count(item_type)

        if not combine_until and item_owned < amount:
            await interaction.followup.send(
                "You dont have this many keys to combine.",
                ephemeral=True,
            )
            return

        combine_amount = amount

        if combine_until:
            combine_amount = max(0, item_owned - amount)

        combine_amount -= combine_amount % 3

        if combine_amount == 0:
            await interaction.followup.send(
                "No keys were combined.",
                ephemeral=True,
            )
            return

        guild_level = await self.database.get_guild_level(guild_id)

        key_level = BaseKey.LVL_MAP[item_type]
        combined_type = BaseKey.TYPE_MAP[key_level + 1]
        return_amount = int(combine_amount / 3)

        if key_level is None or guild_level <= key_level:
            await interaction.followup.send(
                "You cannot combine keys of this level.",
                ephemeral=True,
            )
            return

        self.controller.detach_view_by_id(request.view_id)
        message = await interaction.original_response()
        await message.delete()

        event = InventoryEvent(
            datetime.datetime.now(),
            guild_id,
            user_id,
            item_type,
            -combine_amount,
        )
        await self.controller.dispatch_event(event)

        event = InventoryEvent(
            datetime.datetime.now(),
            guild_id,
            user_id,
            combined_type,
            return_amount,
        )
        await self.controller.dispatch_event(event)

        await interaction.followup.send(
            f"You successfully combined **{combine_amount}** keys of **level {key_level}** into **{return_amount}** key(s) of **level {key_level + 1}**",
            ephemeral=True,
        )

    async def submit_user_view(
        self,
        interaction: discord.Interaction,
        target: discord.Member,
        item: Item,
        view_id: int,
    ):
        guild_id = interaction.guild_id
        user_id = interaction.user.id
        beans_role = await self.settings_manager.get_beans_role(guild_id)

        self.controller.detach_view_by_id(view_id)
        message = await interaction.original_response()
        await message.delete()

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

                if beans_role is not None and beans_role not in [
                    role.id for role in target.roles
                ]:
                    role_name = interaction.guild.get_role(beans_role).name
                    await interaction.followup.send(
                        f"This user does not have the `{role_name}` role.",
                        ephemeral=True,
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

    async def encounter_check(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        member_id = interaction.user.id
        encounters = await self.database.get_encounter_participants(guild_id)

        for _, participants in encounters.items():
            if member_id in participants:
                await interaction.followup.send(
                    "You cannot use this while you are in combat.",
                    ephemeral=True,
                )
                return False
        return True

    async def inventory_check(self, interaction: discord.Interaction, item: Item):
        guild_id = interaction.guild.id
        member_id = interaction.user.id

        inventory = await self.item_manager.get_user_inventory(guild_id, member_id)
        item_owned = inventory.get_item_count(item.type)

        if item_owned == 0:
            await interaction.followup.send(
                "You dont have enough items of this type.",
                ephemeral=True,
            )
            return False

        return True

    async def submit_confirm_view(
        self,
        interaction: discord.Interaction,
        item: Item,
        view_id: int,
    ):
        guild_id = interaction.guild_id
        user_id = interaction.user.id

        boss_key_map = {
            ItemType.DADDY_KEY: EnemyType.DADDY_P1,
            ItemType.WEEB_KEY: EnemyType.WEEB_BALL,
        }
        boss_lvl_map = {
            ItemType.DADDY_KEY: 3,
            ItemType.WEEB_KEY: 6,
        }
        self.controller.detach_view_by_id(view_id)
        message = await interaction.original_response()
        await message.delete()

        match item.type:
            case (
                ItemType.ENCOUNTER_KEY_1
                | ItemType.ENCOUNTER_KEY_2
                | ItemType.ENCOUNTER_KEY_3
                | ItemType.ENCOUNTER_KEY_4
                | ItemType.ENCOUNTER_KEY_5
                | ItemType.ENCOUNTER_KEY_6
            ):
                if not await self.encounter_check(interaction):
                    return
                if not await self.inventory_check(interaction, item):
                    return
                level_map = {v: k for k, v in BaseKey.TYPE_MAP.items()}
                await self.encounter_manager.spawn_encounter(
                    interaction.guild,
                    None,
                    level_map[item.type],
                    owner_id=user_id,
                )

                event = InventoryEvent(
                    datetime.datetime.now(),
                    guild_id,
                    user_id,
                    item.type,
                    -1,
                )
                await self.controller.dispatch_event(event)

                await interaction.followup.send(
                    "Encounter successfully spawned.",
                    ephemeral=True,
                )

            case ItemType.DADDY_KEY | ItemType.WEEB_KEY:
                if not await self.encounter_check(interaction):
                    return
                await self.encounter_manager.spawn_encounter(
                    interaction.guild,
                    boss_key_map[item.type],
                    boss_lvl_map[item.type],
                    owner_id=user_id,
                )

                event = InventoryEvent(
                    datetime.datetime.now(),
                    guild_id,
                    user_id,
                    item.type,
                    -1,
                )
                await self.controller.dispatch_event(event)

                await interaction.followup.send(
                    "Encounter successfully spawned.",
                    ephemeral=True,
                )

    async def item_action(
        self,
        request: InventoryItemAction,
    ):
        interaction = request.interaction
        item_type = request.item_type
        item_action = request.item_action
        view_id = request.view_id

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

    async def open_shop(
        self,
        interaction: discord.Interaction,
        view_id: int,
    ):
        items = await self.item_manager.get_shop_items(interaction.guild_id)

        embed = ShopEmbed(self.bot, interaction.guild.name, items)
        view = ShopView(self.controller, interaction, items)

        user_balance = await self.database.get_member_beans(
            interaction.guild.id, interaction.user.id
        )
        user_items = await self.database.get_item_counts_by_user(
            interaction.guild.id, interaction.user.id
        )

        shop_img = discord.File("./img/shop.png", "shop.png")

        message = await interaction.original_response()
        await message.edit(embed=embed, view=view, attachments=[shop_img])
        view.set_message(message)
        await view.refresh_ui(user_balance=user_balance, user_items=user_items)
        self.controller.detach_view_by_id(view_id)
