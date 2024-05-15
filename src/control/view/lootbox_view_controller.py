import datetime
import random

import discord
from bot_util import BotUtil
from datalayer.database import Database
from datalayer.types import ItemTrigger
from discord.ext import commands
from events.beans_event import BeansEvent
from events.inventory_event import InventoryEvent
from events.jail_event import JailEvent
from events.lootbox_event import LootBoxEvent
from events.types import BeansEventType, JailEventType, LootBoxEventType, UIEventType
from events.ui_event import UIEvent
from items.item import Item
from items.types import ItemType

from control.controller import Controller
from control.event_manager import EventManager
from control.item_manager import ItemManager
from control.jail_manager import JailManager
from control.logger import BotLogger
from control.view.view_controller import ViewController


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
        self.item_manager: ItemManager = controller.get_service(ItemManager)
        self.event_manager: EventManager = controller.get_service(EventManager)
        self.jail_manager: JailManager = self.controller.get_service(JailManager)

    async def listen_for_ui_event(self, event: UIEvent):
        match event.type:
            case UIEventType.CLAIM_LOOTBOX:
                interaction = event.payload[0]
                owner_id = event.payload[1]
                await self.handle_lootbox_claim(interaction, owner_id, event.view_id)

    async def lootbox_checks(self, interaction: discord.Interaction,   owner_id: int) -> bool:
        guild_id = interaction.guild_id
        member_id = interaction.user.id

        stun_base_duration = (await self.item_manager.get_item(guild_id, ItemType.BAT)).value
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

    async def handle_mimic(self, interaction: discord.Interaction, embed: discord.Embed, beans: int) -> tuple[bool,bool]:
        guild_id = interaction.guild_id
        member_id = interaction.user.id

        large_mimic = False
        mimic_detetor = False
        beans_taken = beans

        user_items = await self.item_manager.get_user_items_activated(guild_id, member_id, ItemTrigger.MIMIC)

        if ItemType.MIMIC_DETECTOR in [item.type for item in user_items]:
            message = (
                "**Oh, wait a second!**\nYou feel something tugging on your leg. It's the Foxgirl you found and took care of until now. " 
                "She is signaling you **not to open that chest**, looks like its a **mimic**! Whew that was close. Before you get to thank her, "
                "she runs away and disappears between the trees."
            )
            await interaction.followup.send(content=message, ephemeral=True)
            event = InventoryEvent(datetime.datetime.now(), guild_id, member_id, ItemType.MIMIC_DETECTOR, -1)
            await self.controller.dispatch_event(event)
            mimic_detetor = True
            return large_mimic, mimic_detetor, beans_taken

        bean_balance = await self.database.get_member_beans(guild_id, member_id)
        season_high_score = await self.database.get_member_beans_rankings(guild_id, member_id)

        threshold = int(season_high_score / 10)
        if abs(beans) > threshold:
            beans_taken = -threshold

        if bean_balance + beans_taken < 0:
            beans_taken = -bean_balance

        if beans < -100:
            if ItemType.PROTECTION in [item.type for item in user_items]:
                event = InventoryEvent(datetime.datetime.now(), guild_id, member_id, ItemType.PROTECTION, -1)
                await self.controller.dispatch_event(event)
                embed.add_field(
                    name="Oh no, it's a LARGE Mimic!",
                    value=f"It munches away at your beans, eating `🅱️{abs(beans_taken)}` of them. \nLuckily your Hazmat Suit protects you from further harm. \n(You lose one stack)",
                    inline=False,
                )
                return large_mimic, mimic_detetor, beans_taken

            embed.add_field(
                name="Oh no, it's a LARGE Mimic!",
                value=f"It munches away at your beans, eating `🅱️{abs(beans_taken)}` of them. \nIt swallows your whole body and somehow you end up in JAIL?!?",
                inline=False,
            )
            large_mimic = True
            return large_mimic, mimic_detetor, beans_taken

        embed.add_field(
            name="Oh no, it's a Mimic!",
            value=f"It munches away at your beans, eating `🅱️{abs(beans_taken)}` of them.",
            inline=False,
        )

        return large_mimic, mimic_detetor, beans_taken

    async def handle_lootbox_claim(
        self, interaction: discord.Interaction, owner_id: int, view_id: int
    ):
        event = UIEvent(UIEventType.STOP_INTERACTIONS, None, view_id)
        await self.controller.dispatch_ui_event(event)

        guild_id = interaction.guild_id
        member_id = interaction.user.id

        if not await self.lootbox_checks(interaction, owner_id):
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
        embed.set_image(url="attachment://treasure_open.png")
        attachment = discord.File("./img/treasure_open.png", "treasure_open.png")

        beans = loot_box.beans
        large_mimic = False
        mimic_detector = False

        if beans < 0:
            large_mimic, mimic_detector, beans_taken = await self.handle_mimic(interaction, embed, beans)
            
            if mimic_detector:
                event = UIEvent(UIEventType.RESUME_INTERACTIONS, None, view_id)
                await self.controller.dispatch_ui_event(event)
                return

            beans = beans_taken
                
            embed.set_image(url="attachment://mimic.gif")
            attachment = discord.File("./img/mimic.gif", "mimic.gif")

        elif beans > 0:
            embed.add_field(
                name="A Bunch of Beans!",
                value=f"A whole  `🅱️{beans}` of them.",
                inline=False,
            )

        self.controller.detach_view_by_id(view_id)

        log_message = f"{interaction.user.display_name} claimed a loot box containing {beans} beans"

        items_to_give: list[tuple[int, Item]] = []

        if loot_box.items is not None and len(loot_box.items) > 0:
            embed.add_field(name="Woah, Shiny Items!", value="", inline=False)

            for item_type, amount in loot_box.items.items():
                item = await self.item_manager.get_item(guild_id, item_type)
                item_count = item.base_amount * amount
                item.add_to_embed(self.bot, embed, 43, count=item_count, show_price=False)
                log_message += f" and {item_count}x {item.name}"
                items_to_give.append((item_count, item))

        self.logger.log(interaction.guild_id, log_message, cog="Beans")

        await interaction.edit_original_response(
            embed=embed, view=None, attachments=[attachment]
        )

        event_type = LootBoxEventType.CLAIM
        if owner_id is not None:
            event_type = LootBoxEventType.OPEN

        event = LootBoxEvent(
            datetime.datetime.now(), guild_id, loot_box.id, member_id, event_type
        )
        await self.controller.dispatch_event(event)

        if beans != 0:
            event = BeansEvent(
                datetime.datetime.now(),
                guild_id,
                BeansEventType.LOOTBOX_PAYOUT,
                member_id,
                beans,
            )
            await self.controller.dispatch_event(event)

        for amount, item in items_to_give:
            await self.item_manager.give_item(guild_id, member_id, item, amount)

        if large_mimic:
            jail_announcement = f"<@{member_id}> delved too deep looking for treasure and got sucked into a wormhole that teleported them into jail."
            duration = random.randint(1*60, 3*60)
            member = interaction.user
            success = await self.jail_manager.jail_user(
                guild_id, self.bot.user.id, member, duration
            )
            if not success:
                time_now = datetime.datetime.now()
                affected_jails = await self.database.get_active_jails_by_member(guild_id, member.id)
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
                    remaining = await self.jail_manager.get_jail_remaining(affected_jails[0])
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
