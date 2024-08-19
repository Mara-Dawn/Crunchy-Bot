import datetime
import random

import discord
from discord.ext import commands

from bot_util import BotUtil
from control.controller import Controller
from control.event_manager import EventManager
from control.item_manager import ItemManager
from control.jail_manager import JailManager
from control.logger import BotLogger
from control.service import Service
from control.settings_manager import SettingsManager
from datalayer.database import Database
from datalayer.interaction_modifiers import InteractionModifiers
from datalayer.types import UserInteraction
from events.bat_event import BatEvent
from events.bot_event import BotEvent
from events.inventory_event import InventoryEvent

# needed for global access
from events.jail_event import JailEvent
from items import *  # noqa: F403
from items.item import Item
from items.types import ItemGroup, ItemType


class InteractionManager(Service):

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
        self.item_manager: ItemManager = self.controller.get_service(ItemManager)
        self.event_manager: EventManager = self.controller.get_service(EventManager)
        self.log_name = "Interactions"

    async def listen_for_event(self, event: BotEvent):
        pass

    def __get_already_used_msg(
        self, interaction_type: UserInteraction, user: discord.Member
    ) -> str:
        match interaction_type:
            case UserInteraction.SLAP:
                return f"\n You already slapped {user.display_name}, no extra time will be added this time."
            case UserInteraction.PET:
                return f"\n You already gave {user.display_name} pets, no extra time will be added this time."
            case UserInteraction.FART:
                return f"\n{user.display_name} already enjoyed your farts, no extra time will be added this time."

    def __get_already_used_log_msg(
        self,
        interaction_type: UserInteraction,
        interaction: discord.Interaction,
        user: discord.Member,
    ) -> str:
        match interaction_type:
            case UserInteraction.SLAP:
                return f"User {user.display_name} was already slapped by {interaction.user.display_name}. No extra time will be added."
            case UserInteraction.PET:
                return f"User {user.display_name} already recieved pats from {interaction.user.display_name}. No extra time will be added."
            case UserInteraction.FART:
                return f"User {user.display_name} already enjoyed {interaction.user.display_name}'s farts. No extra time will be added."

    async def get_jail_item_modifiers(
        self,
        interaction: discord.Interaction,
        active_items: list[Item],
        already_interacted: bool,
        self_target: bool,
    ) -> tuple[InteractionModifiers, str, list[Item]]:
        response = ""
        modifiers = InteractionModifiers()
        guild_id = interaction.guild_id
        user_id = interaction.user.id
        items_used = []

        if self_target:
            return (modifiers, response, items_used)

        for item in active_items:
            if item.group == ItemGroup.BONUS_ATTEMPT:
                modifiers.bonus_attempt = item
            if item.group == ItemGroup.MAJOR_JAIL_ACTION:
                modifiers.major_jail_actions.append(item)

        if len(modifiers.major_jail_actions) > 0:
            return (
                modifiers,
                response,
                items_used,
            )

        if already_interacted and modifiers.bonus_attempt is None:
            return (modifiers, response, items_used)

        modifiers.item_modifier = 0

        for item in active_items:
            message, use_item = await self.use_jail_item(
                modifiers, item, guild_id, user_id
            )
            response += message
            if use_item:
                items_used.append(item)

        if modifiers.item_modifier == 0:
            modifiers.item_modifier = 1

        return (modifiers, response, items_used)

    async def get_jail_target_item_modifiers(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        command_type: UserInteraction,
        amount: int,
    ) -> tuple[float, str]:
        user_items = await self.item_manager.get_user_items_activated_by_interaction(
            interaction.guild_id, user.id, command_type
        )
        response = ""
        reduction = 1
        flat_bonus = 0
        for item in user_items:

            if item.group not in [ItemGroup.PROTECTION, ItemGroup.INCOMING_FLAT_BONUS]:
                continue

            match item.group:
                case ItemGroup.PROTECTION:
                    if amount <= 0:
                        continue
                    reduction *= 1 - item.value
                case ItemGroup.INCOMING_FLAT_BONUS:
                    if command_type == UserInteraction.PET:
                        flat_bonus -= item.value
                    else:
                        flat_bonus += item.value
                case _:
                    continue

            if not item.permanent:
                event = InventoryEvent(
                    datetime.datetime.now(),
                    interaction.guild_id,
                    user.id,
                    item.type,
                    -1,
                )
                await self.controller.dispatch_event(event)

            self.logger.log(
                interaction.guild_id,
                f"Item {item.name} was used.",
                cog=self.log_name,
            )
            response += f"* {item.name}\n"

        return (reduction, flat_bonus, response)

    async def user_command_interaction(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        command_type: UserInteraction,
        active_items: list[Item],
    ) -> tuple[str, list[Item]]:
        guild_id = interaction.guild_id

        affected_jail = await self.jail_manager.get_active_jail(guild_id, user)
        if affected_jail is None:
            return "", []

        already_interacted = await self.event_manager.has_jail_event_from_user(
            affected_jail.id, guild_id, interaction.user.id, command_type
        )
        self_target = interaction.user.id == user.id

        modifiers, user_item_info, items_used = await self.get_jail_item_modifiers(
            interaction, active_items, already_interacted, self_target
        )

        if already_interacted:
            if modifiers.bonus_attempt is None:
                self.logger.log(
                    guild_id,
                    self.__get_already_used_log_msg(command_type, interaction, user),
                    cog=self.log_name,
                )
                return self.__get_already_used_msg(command_type, user), []

            items_used.append(modifiers.bonus_attempt)

            self.logger.log(
                interaction.guild_id,
                f"Item {modifiers.bonus_attempt.name} was used.",
                cog=self.log_name,
            )
            user_item_info += f"* {modifiers.bonus_attempt.name}\n"

        response = "\n"
        if user_item_info != "":
            response += "__Items used:__\n" + user_item_info

        amount = 0
        max_amount = None

        match command_type:
            case UserInteraction.SLAP:
                amount = await self.settings_manager.get_jail_slap_time(
                    interaction.guild_id
                )
                amount = amount + modifiers.flat_bonus
            case UserInteraction.PET:
                amount = -await self.settings_manager.get_jail_pet_time(
                    interaction.guild_id
                )
                amount = amount - modifiers.flat_bonus
            case UserInteraction.FART:
                min_amount = (
                    0
                    if modifiers.stabilized
                    else await self.settings_manager.get_jail_fart_min(
                        interaction.guild_id
                    )
                )
                max_amount = await self.settings_manager.get_jail_fart_max(
                    interaction.guild_id
                )
                amount = random.randint(min_amount, max_amount)
                if modifiers.advantage:
                    amount_advantage = random.randint(min_amount, max_amount)
                    amount = max(amount, amount_advantage)
                amount = amount + modifiers.flat_bonus

        reduction, flat_inc_bonus, tartget_item_info = (
            await self.get_jail_target_item_modifiers(
                interaction, user, command_type, amount
            )
        )

        amount += flat_inc_bonus

        if command_type == UserInteraction.FART and max_amount is not None:
            amount = min(max_amount, amount)

        initial_amount = amount

        remaining = await self.jail_manager.get_jail_remaining(affected_jail)
        amount = int(amount * modifiers.item_modifier)
        amount = max(amount, -int(remaining + 1))

        crit_mod = await self.settings_manager.get_jail_base_crit_mod(
            interaction.guild_id
        )
        crit_rate = await self.settings_manager.get_jail_base_crit_rate(
            interaction.guild_id
        )

        is_crit = (random.random() <= crit_rate) or modifiers.auto_crit

        if is_crit:
            response += "**CRITICAL HIT!!!** \n"
            amount = int(amount * crit_mod)

        satan_release = False
        if modifiers.satan_boost and random.random() <= 0.75:
            success = await self.jail_manager.jail_user(
                interaction.guild_id, interaction.user.id, interaction.user, amount
            )

            if not success:
                modifiers.satan_boost = False

            timestamp_now = int(datetime.datetime.now().timestamp())
            satan_release = timestamp_now + (amount * 60)

        if tartget_item_info != "":
            response += "__Items used by target:__\n" + tartget_item_info

        amount = int(amount * reduction)

        damage_info = f"*({initial_amount})*" if initial_amount != amount else ""

        if amount == 0 and is_crit:
            response += f"{interaction.user.display_name} farted so hard, they blew {user.display_name} out of Jail. They are free!\n"
            response += await self.jail_manager.release_user(
                guild_id, interaction.user.id, user
            )

            if not response:
                response += f"Something went wrong, user {user.display_name} could not be released."
        else:
            time_readable = BotUtil.strfdelta(abs(amount), inputtype="minutes")
            if amount >= 0:
                response += f"Their jail sentence was increased by `{time_readable}` {damage_info}. "
            elif amount < 0:
                response += f"Their jail sentence was reduced by `{time_readable}` {damage_info}. "

            time_now = datetime.datetime.now()
            event = JailEvent(
                time_now,
                guild_id,
                command_type,
                interaction.user.id,
                amount,
                affected_jail.id,
            )
            await self.controller.dispatch_event(event)

            remaining = await self.jail_manager.get_jail_remaining(affected_jail)
            response += (
                f'`{BotUtil.strfdelta(remaining, inputtype="minutes")}` still remain.'
            )

        if modifiers.satan_boost and satan_release:
            response += f"\n<@{interaction.user.id}> pays the price of making a deal with the devil and goes to jail as well. They will be released <t:{satan_release}:R>."

        return response, items_used

    async def use_jail_item(
        self, modifiers: InteractionModifiers, item: Item, guild_id: int, user_id: int
    ):
        consume_item = False
        match item.group:
            case ItemGroup.VALUE_MODIFIER:
                if item.type == ItemType.SATAN_FART:
                    affected_jails = await self.database.get_active_jails_by_member(
                        guild_id, user_id
                    )
                    if len(affected_jails) > 0:
                        return "", consume_item
                    modifiers.satan_boost = True
                modifiers.item_modifier += item.value
            case ItemGroup.AUTO_CRIT:
                modifiers.auto_crit = item.value
            case ItemGroup.STABILIZER:
                modifiers.stabilized = item.value
            case ItemGroup.ADVANTAGE:
                modifiers.advantage = item.value
            case ItemGroup.FLAT_BONUS:
                modifiers.flat_bonus += item.value
            case _:
                return "", consume_item

        if not item.permanent:
            consume_item = True

        self.logger.log(
            guild_id,
            f"Item {item.name} was used.",
            cog=self.log_name,
        )
        return f"* {item.name}\n", consume_item

    async def handle_major_action_items(
        self, items: list[Item], member: discord.Member, target_user: discord.Member
    ):
        response = ""

        if member.id == target_user.id or target_user.id == self.bot.user.id:
            return response

        for item in items:
            if item.group == ItemGroup.MAJOR_JAIL_ACTION:
                affected_jail = await self.jail_manager.get_active_jail(
                    target_user.guild.id, target_user
                )
                if affected_jail is None:
                    continue

            item_text = ""
            match item.type:
                case ItemType.ULTRA_PET:
                    release_msg = await self.jail_manager.release_user(
                        member.guild.id, member.id, target_user
                    )
                    if not release_msg:
                        continue

                    item_text += f"<@{target_user.id}> was released from Jail."
                    item_text += release_msg + "\n"

                case ItemType.ULTRA_SLAP:
                    event = BatEvent(
                        datetime.datetime.now(),
                        member.guild.id,
                        member.id,
                        target_user.id,
                        item.value,
                    )
                    await self.controller.dispatch_event(event)

                    item_text += f"<@{target_user.id}> was erased from this dimension and will be stunned for `{BotUtil.strfdelta(item.value, inputtype='minutes')}`."
                    item_text += "\n"

                case ItemType.PENETRATING_PET:
                    item_count = 0
                    inventory_items = await self.database.get_item_counts_by_user(
                        member.guild.id, target_user.id
                    )

                    protection_type = ItemType.PROTECTION

                    if protection_type in inventory_items:
                        item_count = inventory_items[protection_type]

                    if item_count <= 0:
                        continue

                    event = InventoryEvent(
                        datetime.datetime.now(),
                        member.guild.id,
                        target_user.id,
                        protection_type,
                        -item_count,
                    )
                    await self.controller.dispatch_event(event)

                    item_text += f"<@{target_user.id}> was touched by <@{member.id}>'s greasy gamer hands. All of their protection melts away, exposing them to the elements."
                    item_text += "\n"

                case ItemType.SWAP_SLAP:
                    target_jail = await self.jail_manager.get_active_jail(
                        member.guild.id, target_user
                    )

                    if target_jail is not None:
                        continue

                    jail = await self.jail_manager.get_active_jail(
                        member.guild.id, member
                    )

                    if jail is None:
                        continue

                    remaining = await self.jail_manager.get_jail_remaining(jail)

                    await self.jail_manager.release_user(
                        member.guild.id, member.id, member
                    )

                    await self.jail_manager.jail_user(
                        member.guild.id, member.id, target_user, remaining
                    )

                    item_text += f"<@{member.id}> pulls a Uno Reverse Card on <@{target_user.id}>, swapping places with them in jail.\n"
                    item_text += f"They will have to sit out the remaining sentence of `{BotUtil.strfdelta(remaining, inputtype='minutes')}`."
                    item_text += "\n"

            emoji = item.emoji
            if isinstance(item.emoji, int):
                emoji = str(self.bot.get_emoji(item.emoji))
            response += f"\n\n**{emoji} {item.name} {emoji} was used.**\n"
            response += item_text

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
        return response
