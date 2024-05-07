import datetime
import random
import secrets

import discord
from bot_util import BotUtil
from datalayer.database import Database
from datalayer.inventory import UserInventory
from datalayer.lootbox import LootBox
from datalayer.types import ItemTrigger, LootboxType, UserInteraction
from discord.ext import commands
from events.beans_event import BeansEvent
from events.bot_event import BotEvent
from events.inventory_event import InventoryEvent
from events.lootbox_event import LootBoxEvent
from events.notification_event import NotificationEvent
from events.types import BeansEventType, LootBoxEventType

# needed for global access
from items import *  # noqa: F403
from items.item import Item
from items.types import ItemState, ItemType
from view.lootbox_view import LootBoxView

from control.controller import Controller
from control.logger import BotLogger
from control.service import Service
from control.settings_manager import SettingsManager


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

    async def get_shop_items(self, guild_id: int) -> list[Item]:
        items = [x for x in ItemType]
        output = []
        for item_type in items:
            item = await self.get_item(guild_id, item_type)
            if not item.hide_in_shop:
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
            ItemType.CRAPPY_COUPON,
        ]

        lucky_item_pool = [
            ItemType.SATAN_FART,
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
            ItemType.CRAPPY_COUPON,
        ]

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

        # Spawn Chances
        mimic_chance = 0.1
        large_chest_chance = 0.02
        large_mimic_chance = 0.02
        lucky_item_chance = 0.02

        # Chest Ranges
        small_min_beans = 30
        small_max_beans = 80
        large_min_beans = 500
        large_max_beans = 800
        beans = 0
        random_items = {}

        force_roll = None

        if force_type is not None:
            match force_type:
                case LootboxType.SMALL_MIMIC:
                    force_roll = mimic_chance
                case LootboxType.BEANS:
                    force_roll = mimic_chance + large_chest_chance
                case LootboxType.LARGE_MIMIC:
                    force_roll = mimic_chance + large_chest_chance + large_mimic_chance
                case LootboxType.LUCKY_ITEM:
                    force_roll = (
                        mimic_chance
                        + large_chest_chance
                        + large_mimic_chance
                        + lucky_item_chance
                    )
                case LootboxType.REGULAR:
                    force_roll = 1

        for _ in range(size):
            roll = random.random()

            if force_roll is not None:
                roll = force_roll

            small_beans_reward = random.randint(small_min_beans, small_max_beans)
            large_beans_reward = random.randint(large_min_beans, large_max_beans)

            if roll <= mimic_chance:
                beans += -small_beans_reward
            elif roll > mimic_chance and roll <= (mimic_chance + large_chest_chance):
                beans += large_beans_reward
            elif roll > (mimic_chance + large_chest_chance) and roll <= (
                mimic_chance + large_chest_chance + large_mimic_chance
            ):
                beans += -large_beans_reward
            elif roll > (
                mimic_chance + large_chest_chance + large_mimic_chance
            ) and roll <= (
                mimic_chance
                + large_chest_chance
                + large_mimic_chance
                + lucky_item_chance
            ):
                item_type = random.choices(lucky_item_pool, weights=lucky_weights)[0]
                BotUtil.dict_append(random_items, item_type, 1)
            elif roll > (
                mimic_chance
                + large_chest_chance
                + large_mimic_chance
                + lucky_item_chance
            ):
                item_type = random.choices(item_pool, weights=weights)[0]
                BotUtil.dict_append(random_items, item_type, 1)

        return LootBox(guild_id, random_items, beans)

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
        self, interaction: discord.Interaction, size: int = 1
    ):
        member_id = interaction.user.id
        guild_id = interaction.guild_id

        log_message = f"Loot box was dropped in {interaction.guild.name}."
        self.logger.log(guild_id, log_message, cog="Beans")

        loot_box = await self.create_loot_box(guild_id, size=size)

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

        inventory_items = []

        for item_type in item_data:
            item = await self.get_item(guild_id, item_type)
            inventory_items.append(item)

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
                datetime.datetime.now(),
                guild_id,
                member_id,
                item.type,
                total_amount,
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
                notification = f"<@{user_id}> has redeemed a shitty drawing done by <@{269620844790153218}>."
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
