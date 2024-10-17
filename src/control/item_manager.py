import datetime
import random
import secrets

import discord
from discord.ext import commands

from bot_util import BotUtil
from config import Config
from control.controller import Controller
from control.logger import BotLogger
from control.service import Service
from control.settings_manager import SettingsManager
from datalayer.database import Database
from datalayer.inventory import UserInventory
from datalayer.lootbox import LootBox
from datalayer.types import ItemTrigger, LootboxType, UserInteraction
from events.beans_event import BeansEvent
from events.bot_event import BotEvent
from events.inventory_batchevent import InventoryBatchEvent
from events.inventory_event import InventoryEvent
from events.lootbox_event import LootBoxEvent
from events.notification_event import NotificationEvent
from events.types import BeansEventType, LootBoxEventType

# needed for global access
from items import *  # noqa: F403
from items.item import Item
from items.types import ItemState, ItemType
from view.inventory.confirm_view import InventoryConfirmView
from view.lootbox.view import LootBoxView
from view.shop.user_select_view import ShopUserSelectView


class ItemManager(Service):

    def __init__(
        self,
        bot: commands.Bot,
        logger: BotLogger,
        database: Database,
        controller: Controller,
    ):
        super().__init__(bot, logger, database)
        self.controller = controller
        self.settings_manager: SettingsManager = self.controller.get_service(
            SettingsManager
        )
        self.log_name = "Items"

    async def listen_for_event(self, event: BotEvent):
        pass

    async def get_item(self, guild_id: int, item_type: ItemType) -> Item:

        item = globals()[item_type]
        instance = item(
            await self.settings_manager.get_shop_item_price(guild_id, item_type)
        )

        return instance

    async def get_catalog_items(self, guild_id: int) -> list[Item]:
        items = [x for x in ItemType]
        output = []
        for item_type in items:
            item = await self.get_item(guild_id, item_type)
            if not item.secret and await self.settings_manager.get_shop_item_enabled(
                guild_id, item_type
            ):
                output.append(item)

        output = sorted(
            output,
            key=lambda x: (x.permanent, x.shop_category.value, x.cost),
        )
        return output

    async def get_shop_items(self, guild_id: int) -> list[Item]:
        items = [x for x in ItemType]
        output = []
        for item_type in items:
            item = await self.get_item(guild_id, item_type)
            if (
                not item.hide_in_shop
                and await self.settings_manager.get_shop_item_enabled(
                    guild_id, item_type
                )
            ):
                output.append(item)

        return output

    async def create_loot_box(
        self, guild_id: int, size: int = 1, force_type: LootboxType = None
    ) -> LootBox:
        item_pool = [
            ItemType.AUTO_CRIT,
            ItemType.FART_BOOST,
            ItemType.PET_BOOST,
            ItemType.SLAP_BOOST,
            ItemType.BONUS_FART,
            ItemType.BONUS_PET,
            ItemType.BONUS_SLAP,
            ItemType.GIGA_FART,
            ItemType.FART_STABILIZER,
            ItemType.FARTVANTAGE,
            ItemType.SATAN_FART,
            ItemType.BOX_SEED,
            ItemType.CAT_SEED,
            ItemType.YELLOW_SEED,
            ItemType.BAKED_SEED,
            ItemType.GHOST_SEED,
        ]

        lucky_item_pool = [
            ItemType.ADVANCED_FART_PROTECTION,
            ItemType.ULTRA_FART_BOOST,
            ItemType.ULTRA_PET,
            ItemType.ULTRA_SLAP,
            ItemType.PENETRATING_PET,
            ItemType.SWAP_SLAP,
            ItemType.MIMIC,
            ItemType.CATGIRL,
            ItemType.UNLIMITED_GAMBA,
            ItemType.INSTANT_GAMBA,
            ItemType.MIMIC_DETECTOR,
            ItemType.USEFUL_CATGIRL,
            ItemType.FLASH_SEED,
            ItemType.KEY_SEED,
        ]

        key_item_pool = []
        guild_level = await self.database.get_guild_level(guild_id)
        for key_level, key_type in BaseKey.TYPE_MAP.items():  # noqa: F405
            if guild_level < key_level:
                break
            key_item_pool.append(key_type)

        lucky_item_pool += key_item_pool
        item_pool = item_pool + lucky_item_pool
        random_items = {}

        force_roll = None
        if force_type is not None:
            match force_type:
                case LootboxType.SMALL_MIMIC:
                    force_roll = Config.MIMIC_CHANCE
                case LootboxType.BEANS:
                    force_roll = Config.MIMIC_CHANCE + Config.LARGE_CHEST_CHANCE
                case LootboxType.LARGE_MIMIC:
                    force_roll = (
                        Config.MIMIC_CHANCE
                        + Config.LARGE_CHEST_CHANCE
                        + Config.LARGE_MIMIC_CHANCE
                    )
                case LootboxType.LUCKY_ITEM:
                    force_roll = (
                        Config.MIMIC_CHANCE
                        + Config.LARGE_CHEST_CHANCE
                        + Config.LARGE_MIMIC_CHANCE
                        + Config.LUCKY_ITEM_CHANCE
                    )
                case LootboxType.SPOOKY_MIMIC:
                    force_roll = (
                        Config.MIMIC_CHANCE
                        + Config.LARGE_CHEST_CHANCE
                        + Config.LARGE_MIMIC_CHANCE
                        + Config.LUCKY_ITEM_CHANCE
                        + Config.SPOOK_MIMIC_CHANCE
                    )
                case LootboxType.REGULAR:
                    force_roll = 1
                case LootboxType.KEYS:
                    force_roll = 1
                    item_pool = key_item_pool
                    BotUtil.dict_append(
                        random_items, BaseKey.TYPE_MAP[guild_level], 1
                    )  # noqa: F405

        weights = [(await self.get_item(guild_id, x)).weight for x in item_pool]
        weights = [1.0 / w for w in weights]
        sum_weights = sum(weights)
        weights = [w / sum_weights for w in weights]

        lucky_weights = [
            (await self.get_item(guild_id, x)).weight for x in lucky_item_pool
        ]
        lucky_weights = [1.0 / w for w in lucky_weights]
        sum_lucky_weights = sum(lucky_weights)
        lucky_weights = [w / sum_lucky_weights for w in lucky_weights]

        for _ in range(size):
            roll = random.random()

            if force_roll is not None:
                roll = force_roll

            if roll <= Config.MIMIC_CHANCE:
                item_type = ItemType.CHEST_MIMIC
                BotUtil.dict_append(random_items, item_type, 1)
            elif roll > Config.MIMIC_CHANCE and roll <= (
                Config.MIMIC_CHANCE + Config.LARGE_CHEST_CHANCE
            ):
                item_type = ItemType.CHEST_BEANS
                BotUtil.dict_append(random_items, item_type, 1)
            elif roll > (Config.MIMIC_CHANCE + Config.LARGE_CHEST_CHANCE) and roll <= (
                Config.MIMIC_CHANCE
                + Config.LARGE_CHEST_CHANCE
                + Config.LARGE_MIMIC_CHANCE
            ):
                item_type = ItemType.CHEST_LARGE_MIMIC
                BotUtil.dict_append(random_items, item_type, 1)
            elif roll > (
                Config.MIMIC_CHANCE
                + Config.LARGE_CHEST_CHANCE
                + Config.LARGE_MIMIC_CHANCE
            ) and roll <= (
                Config.MIMIC_CHANCE
                + Config.LARGE_CHEST_CHANCE
                + Config.LARGE_MIMIC_CHANCE
                + Config.LUCKY_ITEM_CHANCE
            ):
                item_type = random.choices(lucky_item_pool, weights=lucky_weights)[0]
                BotUtil.dict_append(random_items, item_type, 1)
            elif roll > (
                Config.MIMIC_CHANCE
                + Config.LARGE_CHEST_CHANCE
                + Config.LARGE_MIMIC_CHANCE
                + Config.LUCKY_ITEM_CHANCE
            ) and roll <= (
                Config.MIMIC_CHANCE
                + Config.LARGE_CHEST_CHANCE
                + Config.LARGE_MIMIC_CHANCE
                + Config.LUCKY_ITEM_CHANCE
                + Config.SPOOK_MIMIC_CHANCE
            ):
                item_type = ItemType.CHEST_SPOOK_MIMIC
                BotUtil.dict_append(random_items, item_type, 1)
            elif roll > (
                Config.MIMIC_CHANCE
                + Config.LARGE_CHEST_CHANCE
                + Config.LARGE_MIMIC_CHANCE
                + Config.LUCKY_ITEM_CHANCE
                + Config.SPOOK_MIMIC_CHANCE
            ):
                item_type = random.choices(item_pool, weights=weights)[0]
                BotUtil.dict_append(random_items, item_type, 1)

        return LootBox(guild_id, random_items)

    async def drop_loot_box(
        self, guild: discord.Guild, channel_id: int, force_type: LootboxType = None
    ):
        log_message = f"Loot box was dropped in {guild.name}."
        self.logger.log(guild.id, log_message, cog="Beans")

        loot_box = await self.create_loot_box(guild.id, force_type=force_type)

        title = "A Random Treasure has Appeared"
        description = "Quick, claim it before anyone else does!"
        embed = discord.Embed(
            title=title, description=description, color=discord.Colour.purple()
        )
        embed.set_image(url="attachment://treasure_closed.png")

        view = LootBoxView(self.controller)

        treasure_close_img = discord.File(
            "./img/treasure_closed.png", "treasure_closed.png"
        )

        channel = guild.get_channel(channel_id)

        message = await channel.send(
            "", embed=embed, view=view, files=[treasure_close_img]
        )

        loot_box.message_id = message.id
        loot_box_id = await self.database.log_lootbox(loot_box)

        event = LootBoxEvent(
            datetime.datetime.now(),
            guild.id,
            loot_box_id,
            self.bot.user.id,
            LootBoxEventType.DROP,
        )
        await self.controller.dispatch_event(event)

    async def drop_private_loot_box(
        self,
        interaction: discord.Interaction,
        size: int = 1,
        lootbox_type: LootboxType = None,
    ):
        member_id = interaction.user.id
        guild_id = interaction.guild_id

        log_message = f"Loot box was dropped in {interaction.guild.name}."
        self.logger.log(guild_id, log_message, cog="Beans")

        loot_box = await self.create_loot_box(
            guild_id, size=size, force_type=lootbox_type
        )

        title = f"{interaction.user.display_name}'s Random Treasure Chest"
        description = f"Only you can claim this, <@{member_id}>!"
        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Colour.purple(),
        )
        embed.set_image(url="attachment://treasure_closed.png")

        view = LootBoxView(self.controller, owner_id=interaction.user.id)

        treasure_close_img = discord.File(
            "./img/treasure_closed.png", "treasure_closed.png"
        )

        message = await interaction.followup.send(
            "",
            embed=embed,
            view=view,
            files=[treasure_close_img],
            ephemeral=True,
        )
        loot_box.message_id = message.id
        loot_box_id = await self.database.log_lootbox(loot_box)

        event = LootBoxEvent(
            datetime.datetime.now(),
            guild_id,
            loot_box_id,
            interaction.user.id,
            LootBoxEventType.BUY,
        )
        await self.controller.dispatch_event(event)

    async def get_user_inventory(self, guild_id: int, user_id: int) -> UserInventory:
        item_data = await self.database.get_item_counts_by_user(guild_id, user_id)

        inventory_items: list[Item] = []

        for item_type in item_data:
            item = await self.get_item(guild_id, item_type)
            inventory_items.append(item)

        inventory_items = sorted(
            inventory_items,
            key=lambda x: (not x.permanent, x.shop_category.value, x.cost),
        )

        balance = await self.database.get_member_beans(guild_id, user_id)
        custom_name_color = await self.database.get_custom_color(guild_id, user_id)
        target_id, bully_emoji = await self.database.get_bully_react(guild_id, user_id)
        bully_target_name = BotUtil.get_name(self.bot, guild_id, target_id, 30)
        display_name = BotUtil.get_name(self.bot, guild_id, user_id, 30)
        item_states = await self.database.get_user_item_states(guild_id, user_id)

        inventory = UserInventory(
            guild_id=guild_id,
            member=user_id,
            member_display_name=display_name,
            items=inventory_items,
            inventory=item_data,
            item_states=item_states,
            balance=balance,
            custom_name_color=custom_name_color,
            bully_target_name=bully_target_name,
            bully_emoji=bully_emoji,
        )

        return inventory

    async def get_user_items_activated_by_interaction(
        self, guild_id: int, user_id: int, action: UserInteraction
    ) -> list[Item]:
        trigger = None

        match action:
            case UserInteraction.FART:
                trigger = ItemTrigger.FART
            case UserInteraction.SLAP:
                trigger = ItemTrigger.SLAP
            case UserInteraction.PET:
                trigger = ItemTrigger.PET

        return await self.get_user_items_activated(guild_id, user_id, trigger)

    async def get_user_items_activated(
        self, guild_id: int, user_id: int, action: ItemTrigger
    ) -> list[Item]:
        inventory_items = await self.database.get_item_counts_by_user(guild_id, user_id)

        item_states = await self.database.get_user_item_states(guild_id, user_id)

        output = []

        for item_type, _ in inventory_items.items():

            if (
                item_type in item_states
                and item_states[item_type] == ItemState.DISABLED
            ):
                continue

            item = await self.get_item(guild_id, item_type)

            if not item.activated(action):
                continue

            output.append(item)

        return output

    async def give_item(
        self,
        guild_id: int,
        member_id: int,
        item: Item,
        amount: int = 1,
        force: bool = False,
    ):
        total_amount = amount

        if not force:
            total_amount *= item.base_amount

        now = datetime.datetime.now()

        match item.type:
            case ItemType.CHEST_BEANS:
                beans = random.randint(LootBox.LARGE_MIN_BEANS, LootBox.LARGE_MAX_BEANS)
                item.description = f"A whole {beans} of them."
                event = BeansEvent(
                    now,
                    guild_id,
                    BeansEventType.LOOTBOX_PAYOUT,
                    member_id,
                    beans,
                )
                await self.controller.dispatch_event(event)
                return item

        if item.max_amount is not None:
            item_count = 0

            inventory_items = await self.database.get_item_counts_by_user(
                guild_id, member_id
            )
            if item.type in inventory_items:
                item_count = inventory_items[item.type]

            total_amount = min(total_amount, (item.max_amount - item_count))

        if total_amount != 0:
            event = InventoryEvent(
                now,
                guild_id,
                member_id,
                item.type,
                total_amount,
            )
            await self.controller.dispatch_event(event)
        return item

    async def give_items(
        self,
        guild_id: int,
        member_id: int,
        items: list[tuple[int, Item]],
        force: bool = False,
    ):
        final_items = []
        for amount, item in items:
            total_amount = amount

            if not force:
                total_amount *= item.base_amount

            if item.max_amount is not None:
                item_count = 0

                inventory_items = await self.database.get_item_counts_by_user(
                    guild_id, member_id
                )
                if item.type in inventory_items:
                    item_count = inventory_items[item.type]

                total_amount = min(total_amount, (item.max_amount - item_count))
            if total_amount != 0:
                final_items.append((total_amount, item.type))

        if len(final_items) > 0:
            event = InventoryBatchEvent(
                datetime.datetime.now(),
                guild_id,
                member_id,
                final_items,
            )

            await self.controller.dispatch_event(event)

    async def get_guild_items_activated(
        self, guild_id: int, trigger: ItemTrigger
    ) -> dict[int, list[Item]]:
        guild_item_counts = await self.database.get_item_counts_by_guild(guild_id)
        items: dict[int, list[Item]] = {}

        for user_id, item_counts in guild_item_counts.items():
            for item_type, count in item_counts.items():

                item = await self.get_item(guild_id, item_type)

                if count <= 0 or not item.activated(trigger):
                    continue

                if user_id not in items:
                    items[user_id] = [item]
                    continue
                items[user_id].append(item)

        return items

    async def consume_trigger_items(self, guild: discord.Guild, trigger: ItemTrigger):
        guild_item_counts = await self.database.get_item_counts_by_guild(guild.id)

        for user_id, item_counts in guild_item_counts.items():
            for item_type, count in item_counts.items():

                item = await self.get_item(guild.id, item_type)

                if count <= 0 or not item.activated(trigger):
                    continue

                amount = 1
                if item_type == ItemType.PRESTIGE_BEAN:
                    amount = count

                await self.use_item(guild, user_id, item_type, amount)

    async def use_item_interaction(
        self, interaction: discord.Interaction, item_type: ItemType, amount: int = 1
    ):

        guild = interaction.guild
        user_id = interaction.user.id

        match item_type:
            case ItemType.SPOOK_BEAN:
                item = await self.get_item(guild.id, item_type)
                embed = item.get_embed(self.bot, show_title=False, show_price=False)

                view = ShopUserSelectView(self.controller, interaction, item, None)
                await view.init()

                message = await interaction.followup.send(
                    "", embed=embed, view=view, ephemeral=True
                )
                view.set_message(message)
                await view.refresh_ui(force_embed=embed)
                return
            case (
                ItemType.DADDY_KEY
                | ItemType.WEEB_KEY
                | ItemType.ENCOUNTER_KEY_1
                | ItemType.ENCOUNTER_KEY_2
                | ItemType.ENCOUNTER_KEY_3
                | ItemType.ENCOUNTER_KEY_4
                | ItemType.ENCOUNTER_KEY_5
                | ItemType.ENCOUNTER_KEY_6
            ):
                item = await self.get_item(guild.id, item_type)
                embed = item.get_embed(self.bot, show_title=False, show_price=False)

                view = InventoryConfirmView(self.controller, interaction, item, None)

                message = await interaction.followup.send(
                    "", embed=embed, view=view, ephemeral=True
                )
                view.set_message(message)
                await view.refresh_ui(force_embed=embed)
                return

        return await self.use_item(guild, user_id, item_type, amount)

    async def use_item(
        self, guild: discord.Guild, user_id: int, item_type: ItemType, amount: int = 1
    ):
        guild_id = guild.id
        time_now = datetime.datetime.now()

        item = await self.get_item(guild.id, item_type)

        if not item.permanent:
            event = InventoryEvent(time_now, guild_id, user_id, item_type, -amount)
            await self.controller.dispatch_event(event)

        match item_type:
            case ItemType.MIMIC:
                bean_channels = await self.settings_manager.get_beans_channels(guild_id)
                if len(bean_channels) == 0:
                    return
                await self.drop_loot_box(
                    guild,
                    secrets.choice(bean_channels),
                    force_type=LootboxType.LARGE_MIMIC,
                )

            case ItemType.CRAPPY_COUPON:
                lusa = self.bot.get_user(269620844790153218)
                member = self.bot.get_user(user_id)
                notification_lusa = f"<@{user_id}> ({member.display_name}) has redeemed a shitty drawing on **{guild.name}**"
                await lusa.send(notification_lusa)

                notification = f"<@{user_id}> has redeemed a shitty drawing. Lusa has been notified."
                event = NotificationEvent(time_now, guild_id, notification)
                await self.controller.dispatch_event(event)

            case ItemType.PRESTIGE_BEAN:
                beans_amount = item.value * amount
                bean_event = BeansEvent(
                    datetime.datetime.now(),
                    guild.id,
                    BeansEventType.PRESTIGE,
                    user_id,
                    beans_amount,
                )
                await self.controller.dispatch_event(bean_event)
