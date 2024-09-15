import datetime
import random
import secrets

import discord
from bot_util import BotUtil
from config import Config
from datalayer.database import Database
from datalayer.lootbox import LootBox
from datalayer.types import ItemTrigger
from discord.ext import commands
from events.beans_event import BeansEvent
from events.inventory_event import InventoryEvent
from events.jail_event import JailEvent
from events.lootbox_event import LootBoxEvent
from events.types import BeansEventType, JailEventType, LootBoxEventType, UIEventType
from events.ui_event import UIEvent
from items import Debuff
from items.item import Item
from items.types import ItemType

from control.controller import Controller
from control.event_manager import EventManager
from control.item_manager import ItemManager
from control.jail_manager import JailManager
from control.logger import BotLogger
from control.settings_manager import SettingsManager
from control.view.view_controller import ViewController


class MimicProtectedException(Exception):
    pass


class LootBoxViewController(ViewController):

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
        self.item_manager: ItemManager = controller.get_service(ItemManager)
        self.event_manager: EventManager = controller.get_service(EventManager)
        self.jail_manager: JailManager = self.controller.get_service(JailManager)

    async def listen_for_ui_event(self, event: UIEvent):
        match event.type:
            case UIEventType.CLAIM_LOOTBOX:
                interaction = event.payload[0]
                owner_id = event.payload[1]
                await self.handle_lootbox_claim(interaction, owner_id, event.view_id)

    async def lootbox_checks(
        self, interaction: discord.Interaction, owner_id: int
    ) -> bool:
        guild_id = interaction.guild_id
        member_id = interaction.user.id

        beans_role = await self.settings_manager.get_beans_role(guild_id)
        if beans_role is not None and beans_role not in [
            role.id for role in interaction.user.roles
        ]:
            role_name = interaction.guild.get_role(beans_role).name
            await interaction.followup.send(
                f"You can only use this feature if you have the role `{role_name}`.",
                ephemeral=True,
            )
            return False

        stun_base_duration = (
            await self.item_manager.get_item(guild_id, ItemType.BAT)
        ).value
        stunned_remaining = await self.event_manager.get_stunned_remaining(
            guild_id, interaction.user.id, stun_base_duration
        )

        if stunned_remaining > 0 and owner_id is None:
            timestamp_now = int(datetime.datetime.now().timestamp())
            remaining = int(timestamp_now + stunned_remaining)
            await interaction.followup.send(
                f"You are currently stunned from a bat attack. Try again <t:{remaining}:R>",
                ephemeral=True,
            )
            return False

        if owner_id is not None and member_id != owner_id:
            await interaction.followup.send(
                "This is a personalized lootbox, only the owner can claim it.",
                ephemeral=True,
            )
            return False
        return True

    async def mimic_detector(
        self,
        interaction: discord.Interaction,
        user_items: list[Item],
        lootbox_size: int,
    ) -> bool:
        guild_id = interaction.guild_id
        member_id = interaction.user.id

        if (
            ItemType.MIMIC_DETECTOR in [item.type for item in user_items]
            and lootbox_size == 1
        ):
            message = (
                "**Oh, wait a second!**\nYou feel something tugging on your leg. It's the Foxgirl you found and took care of until now. "
                "She is signaling you **not to open that chest**, looks like its a **mimic**! Whew that was close. Before you get to thank her, "
                "she runs away and disappears between the trees."
            )
            await interaction.followup.send(content=message, ephemeral=True)
            event = InventoryEvent(
                datetime.datetime.now(),
                guild_id,
                member_id,
                ItemType.MIMIC_DETECTOR,
                -1,
            )
            await self.controller.dispatch_event(event)
            return True

        return False

    async def balance_mimic_beans(
        self, interaction: discord.Interaction, beans: int
    ) -> int:
        guild_id = interaction.guild_id
        member_id = interaction.user.id

        bean_balance = await self.database.get_member_beans(guild_id, member_id)
        season_high_score = await self.database.get_member_beans_rankings(
            guild_id, member_id
        )

        beans_taken = beans

        threshold = int(season_high_score / 10)
        if abs(beans) > threshold:
            beans_taken = -threshold

        if bean_balance + beans_taken < 0:
            beans_taken = -bean_balance

        return beans_taken

    async def mimic_protection(
        self, interaction: discord.Interaction, user_items: list[Item]
    ) -> bool:
        guild_id = interaction.guild_id
        member_id = interaction.user.id

        if ItemType.PROTECTION in [item.type for item in user_items]:
            user_protection = await self.database.get_item_counts_by_user(
                guild_id, member_id, item_types=[ItemType.PROTECTION]
            )

            if ItemType.PROTECTION not in user_protection:
                return False

            user_protection_amount = user_protection[ItemType.PROTECTION]
            amount = min(5, user_protection_amount)
            event = InventoryEvent(
                datetime.datetime.now(),
                guild_id,
                member_id,
                ItemType.PROTECTION,
                -amount,
            )
            await self.controller.dispatch_event(event)
            return True
        return False

    async def mimic_jail_user(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        member_id = interaction.user.id

        jail_announcement = f"<@{member_id}> delved too deep looking for treasure and got sucked into a wormhole that teleported them into jail."
        duration = random.randint(1 * 60, 3 * 60)
        member = interaction.user
        success = await self.jail_manager.jail_user(
            guild_id, self.bot.user.id, member, duration
        )
        if not success:
            time_now = datetime.datetime.now()
            affected_jails = await self.database.get_active_jails_by_member(
                guild_id, member.id
            )
            if len(affected_jails) > 0:
                event = JailEvent(
                    time_now,
                    guild_id,
                    JailEventType.INCREASE,
                    self.bot.user.id,
                    duration,
                    affected_jails[0].id,
                )
                await self.controller.dispatch_event(event)
                remaining = await self.jail_manager.get_jail_remaining(
                    affected_jails[0]
                )
                jail_announcement = f"Trying to escape jail, <@{member_id}> came across a suspiciously large looking chest. Peering inside they got sucked back into their jail cell.\n`{BotUtil.strfdelta(duration, inputtype="minutes")}` have been added to their jail sentence.\n`{BotUtil.strfdelta(remaining, inputtype="minutes")}` still remain."
                await self.jail_manager.announce(interaction.guild, jail_announcement)
            else:
                self.logger.error(
                    guild_id,
                    "User already jailed but no active jail was found.",
                    "Shop",
                )
        else:
            timestamp_now = int(datetime.datetime.now().timestamp())
            release = timestamp_now + (duration * 60)
            jail_announcement += f"\nThey will be released <t:{release}:R>."
            await self.jail_manager.announce(interaction.guild, jail_announcement)

    async def mimic_haunt_user(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        member_id = interaction.user.id

        ghost = secrets.choice(Debuff.DEBUFFS)
        event = InventoryEvent(
            datetime.datetime.now(),
            guild_id,
            member_id,
            ghost,
            Debuff.DEBUFF_DURATION,
        )
        await self.controller.dispatch_event(event)

    async def handle_beans_item(self, item: Item, embed: discord.Embed) -> int:
        beans = random.randint(LootBox.LARGE_MIN_BEANS, LootBox.LARGE_MAX_BEANS)
        item.description = f"A whole {beans} of them."
        item.add_to_embed(
            self.bot, embed, Config.SHOP_ITEM_MAX_WIDTH, count=beans, show_price=False
        )
        return beans

    async def handle_mimic_item(
        self,
        interaction: discord.Interaction,
        user_items: list[Item],
        item: Item,
        embed: discord.Embed,
        lootbox_size: int,
    ) -> int:
        if await self.mimic_detector(interaction, user_items, lootbox_size):
            raise MimicProtectedException
        beans = -random.randint(LootBox.SMALL_MIN_BEANS, LootBox.SMALL_MAX_BEANS)
        beans_taken = await self.balance_mimic_beans(interaction, beans)
        item.description = (
            f"It munches away at your beans, eating {abs(beans_taken)} of them."
        )
        item.add_to_embed(
            self.bot,
            embed,
            Config.SHOP_ITEM_MAX_WIDTH,
            count=beans_taken,
            show_price=False,
        )
        return beans_taken

    async def handle_large_mimic_item(
        self,
        interaction: discord.Interaction,
        user_items: list[Item],
        item: Item,
        embed: discord.Embed,
        lootbox_size: int,
    ) -> tuple[int, int]:
        jailings = 0
        if await self.mimic_detector(interaction, user_items, lootbox_size):
            raise MimicProtectedException
        beans = -random.randint(LootBox.LARGE_MIN_BEANS, LootBox.LARGE_MAX_BEANS)
        beans_taken = await self.balance_mimic_beans(interaction, beans)
        if await self.mimic_protection(interaction, user_items):
            item.description = f"It munches away at your beans, eating {abs(beans_taken)} of them. Luckily your Hazmat Suit protects you from further harm. \n(You lose five stacks)"
        else:
            item.description = f"It munches away at your beans, eating {abs(beans_taken)} of them. It swallows your whole body and somehow you end up in JAIL?!?"
            jailings += 1
        item.add_to_embed(
            self.bot,
            embed,
            Config.SHOP_ITEM_MAX_WIDTH,
            count=beans_taken,
            show_price=False,
        )
        return jailings, beans_taken

    async def handle_spook_mimic_item(
        self,
        interaction: discord.Interaction,
        user_items: list[Item],
        item: Item,
        embed: discord.Embed,
        lootbox_size: int,
    ) -> int:
        if await self.mimic_detector(interaction, user_items, lootbox_size):
            raise MimicProtectedException
        beans = -random.randint(LootBox.SMALL_MIN_BEANS, LootBox.SMALL_MAX_BEANS)
        beans_taken = await self.balance_mimic_beans(interaction, beans)
        item.description = (
            "A Ghost suddenly jumps out of the chest and possesses you. "
            "Better hope it doesnt do anything ... *weird*.\n"
            f"It also munches away at your beans, eating {abs(beans_taken)} of them."
        )
        item.add_to_embed(
            self.bot,
            embed,
            Config.SHOP_ITEM_MAX_WIDTH,
            count=beans_taken,
            show_price=False,
        )
        return beans_taken

    async def handle_lootbox_items(
        self, interaction: discord.Interaction, loot_box: LootBox, embed: discord.Embed
    ):
        if len(list(LootBox.MIMICS & loot_box.items.keys())) > 0:
            embed.set_image(url="attachment://mimic.gif")
            attachment = discord.File("./img/mimic.gif", "mimic.gif")
        else:
            embed.set_image(url="attachment://treasure_open.png")
            attachment = discord.File("./img/treasure_open.png", "treasure_open.png")

        log_message = f"{interaction.user.display_name} claimed a loot box containing "

        guild_id = interaction.guild_id
        member_id = interaction.user.id

        user_items = await self.item_manager.get_user_items_activated(
            guild_id, member_id, ItemTrigger.MIMIC
        )

        items_to_give: list[tuple[int, Item]] = []
        total_beans = 0

        jailings = 0
        haunts = 0

        if loot_box.items is not None and len(loot_box.items) > 0:
            lootbox_size = len(loot_box.items)
            for item_type, amount in loot_box.items.items():
                item = await self.item_manager.get_item(guild_id, item_type)
                item_count = item.base_amount * amount
                log_message += f"{item_count}x {item.name}, "

                match item_type:
                    case ItemType.CHEST_BEANS:
                        for _ in range(item_count):
                            total_beans += await self.handle_beans_item(item, embed)
                    case ItemType.CHEST_MIMIC:
                        for _ in range(item_count):
                            try:
                                total_beans += await self.handle_mimic_item(
                                    interaction, user_items, item, embed, lootbox_size
                                )
                            except MimicProtectedException:
                                return False
                    case ItemType.CHEST_LARGE_MIMIC:
                        for _ in range(item_count):
                            try:
                                jailing, beans = await self.handle_large_mimic_item(
                                    interaction, user_items, item, embed, lootbox_size
                                )
                                total_beans += beans
                                jailings += jailing
                            except MimicProtectedException:
                                return False
                    case ItemType.CHEST_SPOOK_MIMIC:
                        for _ in range(item_count):
                            try:
                                total_beans += await self.handle_spook_mimic_item(
                                    interaction, user_items, item, embed, lootbox_size
                                )
                                haunts += 1
                            except MimicProtectedException:
                                return False
                    case _:
                        item.add_to_embed(
                            self.bot,
                            embed,
                            Config.SHOP_ITEM_MAX_WIDTH,
                            count=item_count,
                            show_price=False,
                        )
                        items_to_give.append((amount, item))

        await interaction.edit_original_response(
            embed=embed, view=None, attachments=[attachment]
        )
        self.logger.log(interaction.guild_id, log_message, cog="Beans")

        if len(items_to_give) > 0:
            await self.item_manager.give_items(guild_id, member_id, items_to_give)

        bean_balance = await self.database.get_member_beans(guild_id, member_id)
        total_beans = max(total_beans, -bean_balance)

        if total_beans != 0:
            event = BeansEvent(
                datetime.datetime.now(),
                guild_id,
                BeansEventType.LOOTBOX_PAYOUT,
                member_id,
                total_beans,
            )
            await self.controller.dispatch_event(event)

        for _ in range(jailings):
            await self.mimic_jail_user(interaction)
        for _ in range(haunts):
            await self.mimic_haunt_user(interaction)

        return True

    async def handle_lootbox_claim(
        self, interaction: discord.Interaction, owner_id: int, view_id: int
    ):
        event = UIEvent(UIEventType.STOP_INTERACTIONS, None, view_id)
        await self.controller.dispatch_ui_event(event)

        guild_id = interaction.guild_id
        member_id = interaction.user.id

        if not await self.lootbox_checks(interaction, owner_id):
            event = UIEvent(UIEventType.RESUME_INTERACTIONS, None, view_id)
            await self.controller.dispatch_ui_event(event)
            return

        message = await interaction.original_response()
        loot_box = await self.database.get_loot_box_by_message_id(guild_id, message.id)

        title = "A Random Treasure has Appeared"
        if owner_id is not None:
            title = f"{interaction.user.display_name}'s Random Treasure Chest"

        description = f"This treasure was claimed by: \n <@{member_id}>"
        description += "\n\nYou slowly open the chest and reveal..."
        embed = discord.Embed(
            title=title, description=description, color=discord.Colour.purple()
        )

        if not await self.handle_lootbox_items(interaction, loot_box, embed):
            event = UIEvent(UIEventType.RESUME_INTERACTIONS, None, view_id)
            await self.controller.dispatch_ui_event(event)
            return

        self.controller.detach_view_by_id(view_id)

        event_type = LootBoxEventType.CLAIM
        if owner_id is not None:
            event_type = LootBoxEventType.OPEN

        event = LootBoxEvent(
            datetime.datetime.now(), guild_id, loot_box.id, member_id, event_type
        )
        await self.controller.dispatch_event(event)
