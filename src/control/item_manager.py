import datetime
import random

import discord
from bot_util import BotUtil
from datalayer.database import Database
from datalayer.inventory import UserInventory
from datalayer.lootbox import LootBox
from datalayer.types import ItemTrigger, UserInteraction
from discord.ext import commands
from events.bat_event import BatEvent
from events.bot_event import BotEvent
from events.inventory_event import InventoryEvent
from events.lootbox_event import LootBoxEvent
from events.types import LootBoxEventType

# needed for global access
from items import *  # noqa: F403
from items.item import Item
from items.types import ItemType
from view.lootbox_view import LootBoxView

from control.controller import Controller
from control.jail_manager import JailManager
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
        self.jail_manager: JailManager = self.controller.get_service(JailManager)
        self.log_name = "Items"

    async def listen_for_event(self, event: BotEvent):
        pass

    def get_item(self, guild_id: int, item_type: ItemType) -> Item:

        item = globals()[item_type]
        instance = item(self.settings_manager.get_shop_item_price(guild_id, item_type))

        return instance

    def get_shop_items(self, guild_id: int) -> list[Item]:
        items = [x.value for x in ItemType]
        output = []
        for item_type in items:
            item = self.get_item(guild_id, item_type)
            if not item.lootbox_exclusive:
                output.append(item)

        return output

    def create_loot_box(self, guild_id: int) -> LootBox:
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
        ]

        weights = [self.get_item(guild_id, x).weight for x in item_pool]

        # Spawn Chances
        mimic_chance = 0.1
        large_chest_chance = 0.04
        super_mimic_chance = 0.03

        # Chest Ranges
        small_min_beans = 30
        small_max_beans = 80
        large_min_beans = 500
        large_max_beans = 800
        small_beans_reward = random.randint(small_min_beans, small_max_beans)
        large_beans_reward = random.randint(large_min_beans, large_max_beans)
        roll = random.random()

        random_item = None
        if roll <= mimic_chance:
            beans = -small_beans_reward
        elif roll > mimic_chance and roll <= (mimic_chance + large_chest_chance):
            beans = large_beans_reward
        elif roll > (mimic_chance + large_chest_chance) and roll <= (
            mimic_chance + large_chest_chance + super_mimic_chance
        ):
            beans = -large_beans_reward
        elif roll > (mimic_chance + large_chest_chance + super_mimic_chance):
            beans = 0
            weights = [1.0 / w for w in weights]
            sum_weights = sum(weights)
            weights = [w / sum_weights for w in weights]
            random_item = random.choices(item_pool, weights=weights)[0]
        return LootBox(guild_id, random_item, beans)

    async def drop_loot_box(self, guild: discord.Guild, channel_id: int):
        log_message = f"Loot box was dropped in {guild.name}."
        self.logger.log(guild.id, log_message, cog="Beans")

        loot_box = self.create_loot_box(guild.id)

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
        loot_box_id = self.database.log_lootbox(loot_box)

        event = LootBoxEvent(
            datetime.datetime.now(),
            guild.id,
            loot_box_id,
            self.bot.user.id,
            LootBoxEventType.DROP,
        )
        await self.controller.dispatch_event(event)

    def get_user_inventory(self, guild_id: int, user_id: int) -> UserInventory:
        item_data = self.database.get_item_counts_by_user(guild_id, user_id)

        inventory_items = []

        for item_type in item_data:
            item = self.get_item(guild_id, item_type)
            inventory_items.append(item)

        balance = self.database.get_member_beans(guild_id, user_id)
        custom_name_color = self.database.get_custom_color(guild_id, user_id)
        target_id, bully_emoji = self.database.get_bully_react(guild_id, user_id)
        bully_target_name = BotUtil.get_name(self.bot, guild_id, target_id, 30)
        display_name = BotUtil.get_name(self.bot, guild_id, user_id, 30)

        inventory = UserInventory(
            guild_id=guild_id,
            member=user_id,
            member_display_name=display_name,
            items=inventory_items,
            inventory=item_data,
            balance=balance,
            custom_name_color=custom_name_color,
            bully_target_name=bully_target_name,
            bully_emoji=bully_emoji,
        )

        return inventory

    def get_user_items_activated_by_interaction(
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

        return self.get_user_items_activated(guild_id, user_id, trigger)

    def get_user_items_activated(
        self, guild_id: int, user_id: int, action: ItemTrigger
    ) -> list[Item]:
        inventory_items = self.database.get_item_counts_by_user(guild_id, user_id)

        output = []

        for item_type, _ in inventory_items.items():

            item = self.get_item(guild_id, item_type)

            if not item.activated(action):
                continue

            output.append(item)

        return output

    async def handle_major_action_items(
        self, items: list[Item], member: discord.Member, target_user: discord.Member
    ):
        response = ""
        for item in items:
            match item.type:
                case ItemType.ULTRA_PET:
                    release_msg = await self.jail_manager.release_user(
                        member.guild.id, member.id, target_user
                    )
                    if not release_msg:
                        continue
                    response += (
                        f"\n\n**{item.emoji} {item.name} {item.emoji} was used.**\n"
                    )
                    response += f"<@{target_user.id}> was released from Jail."
                    response += release_msg + "\n"
                    event = InventoryEvent(
                        datetime.datetime.now(),
                        member.guild.id,
                        member.id,
                        item.type,
                        -1,
                    )
                    await self.controller.dispatch_event(event)
                    self.logger.log(
                        member.guild.id,
                        f"Item {item.name} was used.",
                        cog=self.log_name,
                    )
                case ItemType.ULTRA_SLAP:
                    event = BatEvent(
                        datetime.datetime.now(),
                        member.guild.id,
                        member.id,
                        target_user.id,
                        item.value,
                    )
                    await self.controller.dispatch_event(event)
                    response += (
                        f"\n\n**{item.emoji} {item.name} {item.emoji} was used.**\n"
                    )
                    response += f"<@{target_user.id}> was erased from this dimension and will be stunned for `{BotUtil.strfdelta(item.value, inputtype='minutes')}`."
                    response += "\n"
        return response

    async def get_guild_items_activated(
        self, guild_id: int, trigger: ItemTrigger
    ) -> dict[int, list[Item]]:
        guild_item_counts = self.database.get_item_counts_by_guild(guild_id)
        items: dict[int, list[Item]] = {}

        for user_id, item_counts in guild_item_counts.items():
            for item_type, count in item_counts.items():

                item = self.get_item(guild_id, item_type)

                if count <= 0 or not item.activated(trigger):
                    continue

                if user_id not in items:
                    items[user_id] = [item]
                    continue
                items[user_id].append(item)

        return items

    async def use_items(self, guild_id: int, trigger: ItemTrigger):
        guild_item_counts = self.database.get_item_counts_by_guild(guild_id)

        for user_id, item_counts in guild_item_counts.items():
            for item_type, count in item_counts.items():

                item = self.get_item(guild_id, item_type)

                if count <= 0 or not item.activated(trigger):
                    continue

                event = InventoryEvent(
                    datetime.datetime.now(), guild_id, user_id, item.type, -1
                )
                await self.controller.dispatch_event(event)
