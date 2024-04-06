from typing import Dict, List
import datetime
import random
import discord
from discord.ext import commands
from bot_util import BotUtil
from control.controller import Controller
from control.service import Service
from control.logger import BotLogger
from control.view.lootbox_view_controller import LootBoxViewController
from datalayer.database import Database
from datalayer.lootbox import LootBox
from datalayer.inventory import UserInventory
from datalayer.types import ItemTrigger, UserInteraction
from view.lootbox_view import LootBoxView
from events.bot_event import BotEvent
from events.inventory_event import InventoryEvent
from events.lootbox_event import LootBoxEvent
from events.types import LootBoxEventType
from items import Item
from items.types import ItemType

# needed for global access
# pylint: disable-next=unused-import,W0614,W0401
from items import *


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
        self.settings_manager = None
        self.log_name = "Items"

    async def listen_for_event(self, event: BotEvent):
        pass

    def get_item(self, guild_id: int, item_type: ItemType) -> Item:

        item = globals()[item_type]
        instance = item(self.settings.get_shop_item_price(guild_id, item_type))

        return instance

    def get_items(self, guild_id: int) -> List[Item]:
        items = [x.value for x in ItemType]
        output = []
        for item_type in items:
            output.append(self.get_item(guild_id, item_type))

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
        ]

        weights = [self.get_item(guild_id, x).get_cost() for x in item_pool]
        chance_for_item = self.settings.get_setting(
            guild_id,
            SettingsManager.BEANS_SUBSETTINGS_KEY,
            SettingsManager.BEANS_LOOTBOX_RARE_CHANCE_KEY,
        )
        mimic_chance = 0.1
        chance_for_bonus_beans = 0.2
        random_item = None

        min_beans = self.settings.get_setting(
            guild_id,
            SettingsManager.BEANS_SUBSETTINGS_KEY,
            SettingsManager.BEANS_LOOTBOX_MIN_BEANS_KEY,
        )
        max_beans = self.settings.get_setting(
            guild_id,
            SettingsManager.BEANS_SUBSETTINGS_KEY,
            SettingsManager.BEANS_LOOTBOX_MAX_BEANS_KEY,
        )

        beans = random.randint(min_beans, max_beans)
        roll = random.random()

        if roll <= chance_for_item:
            weights = [1.0 / w for w in weights]
            sum_weights = sum(weights)
            weights = [w / sum_weights for w in weights]
            random_item = random.choices(item_pool, weights=weights)[0]
        elif roll > chance_for_item and roll <= (
            chance_for_item + chance_for_bonus_beans
        ):
            beans = random.randint(min_beans * 10, max_beans * 10)
        elif roll > 1 - mimic_chance:
            beans = -beans

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
        embed.set_image(url="attachment://treasure_closed.jpg")

        view_controller = self.controller.get_view_controller(LootBoxViewController)
        view = LootBoxView(view_controller)

        treasure_close_img = discord.File(
            "./img/treasure_closed.jpg", "treasure_closed.jpg"
        )

        channel = guild.get_channel(channel_id)

        message = await channel.send(
            "", embed=embed, view=view, files=[treasure_close_img]
        )

        loot_box.set_message_id(message.id)
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

        for item_type in item_data.keys():
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
    ) -> List[Item]:
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
    ) -> List[Item]:
        inventory_items = self.database.get_item_counts_by_user(guild_id, user_id)

        output = []

        for item_type, _ in inventory_items.items():

            item = self.get_item(guild_id, item_type)

            if not item.activated(action):
                continue

            output.append(item)

        return output

    async def get_guild_items_activated(
        self, guild_id: int, trigger: ItemTrigger
    ) -> Dict[int, List[Item]]:
        guild_item_counts = self.database.get_item_counts_by_guild(guild_id)
        items: Dict[int, List[Item]] = {}

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
                    datetime.datetime.now(), guild_id, user_id, item.get_type(), -1
                )
                await self.controller.dispatch_event(event)
