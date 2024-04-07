import traceback

import discord
from discord.ext import commands

from control.controller import Controller
from control.logger import BotLogger
from control.service import Service
from control.settings_manager import SettingsManager
from datalayer.database import Database
from events.bot_event import BotEvent
from events.inventory_event import InventoryEvent
from events.types import EventType
from items.types import ItemType


class RoleManager(Service):

    LOTTERY_ROLE_NAME = "Lottery"
    TIMEOUT_ROLE_NAME = "Timeout"

    def __init__(
        self,
        bot: commands.Bot,
        logger: BotLogger,
        database: Database,
        controller: Controller,
    ):
        super().__init__(bot, logger, database)
        self.controller = controller
        self.settings_manager = self.controller.get_service(SettingsManager)
        self.log_name = "Roles"

    async def listen_for_event(self, event: BotEvent):
        match event.type:
            case EventType.INVENTORY:
                inventory_event: InventoryEvent = event
                match inventory_event.item_type:
                    case ItemType.LOTTERY_TICKET:
                        if inventory_event.amount >= 0:
                            await self.add_lottery_role(
                                inventory_event.guild_id,
                                inventory_event.member_id,
                            )
                        else:
                            await self.remove_lottery_role(
                                inventory_event.guild_id,
                                inventory_event.member_id,
                            )
                    case ItemType.NAME_COLOR:
                        await self.update_username_color(
                            inventory_event.guild_id,
                            inventory_event.member_id,
                        )

    async def get_lottery_role(self, guild: discord.Guild) -> discord.Role:
        lottery_role = discord.utils.get(guild.roles, name=self.LOTTERY_ROLE_NAME)

        if lottery_role is None:
            lottery_role = await guild.create_role(
                name=self.LOTTERY_ROLE_NAME,
                mentionable=True,
                reason="Used to keep track of lottery participants and ping them on a draw.",
            )

        return lottery_role

    async def add_lottery_role(self, guild_id: int, user_id: int) -> discord.Role:
        guild: discord.Guild = self.bot.get_guild(guild_id)
        member: discord.Member = guild.get_member(user_id)
        lottery_role = await self.get_lottery_role(guild)
        try:
            await member.add_roles(lottery_role)
            self.logger.log(
                guild_id,
                f"Added role {self.LOTTERY_ROLE_NAME} to member {member.name}.",
                cog="Beans",
            )
        except discord.Forbidden:
            self.logger.log(
                guild_id,
                f"Missing permissions to change user roles of {member.name}.",
                cog="Beans",
            )
            traceback.print_stack()
            traceback.print_exc()

    async def remove_lottery_role(self, guild_id: int, user_id: int) -> discord.Role:
        guild: discord.Guild = self.bot.get_guild(guild_id)
        member: discord.Member = guild.get_member(user_id)
        lottery_role = await self.get_lottery_role(guild)
        try:
            await member.remove_roles(lottery_role)
            self.logger.log(
                guild_id,
                f"Removed role {self.LOTTERY_ROLE_NAME} from member {member.name}.",
                cog="Beans",
            )
        except discord.Forbidden:
            self.logger.log(
                guild_id,
                f"Missing permissions to change user roles of {member.name}.",
                cog="Beans",
            )
            traceback.print_stack()
            traceback.print_exc()

    async def create_custom_user_role(
        self, guild: discord.Guild, user: discord.Member, color: discord.Color
    ) -> discord.Role:
        custom_role = await guild.create_role(
            name=f"~{user.name}~",
            mentionable=False,
            colour=color,
            reason=f"Custom color role for {user.display_name}.",
        )

        bot_member = guild.get_member(self.bot.user.id)
        bot_roles = bot_member.roles

        bot_max_pos = 0
        for role in bot_roles:
            bot_max_pos = max(bot_max_pos, role.position)
        self.logger.log(guild.id, f"BOT MAX POS:{bot_max_pos}", cog="TEST")
        bot_max_pos -= 1

        user_roles = user.roles
        max_pos = 0
        for role in user_roles:
            max_pos = max(max_pos, role.position)
        self.logger.log(guild.id, f"USER MAX POS:{max_pos}", cog="TEST")
        max_pos += 1

        max_pos = min(bot_max_pos, max_pos)

        self.logger.log(guild.id, f"MAX POS:{max_pos}", cog="TEST")

        await custom_role.edit(position=max_pos)

        self.database.log_custom_role(guild.id, user.id, custom_role.id)

        await user.add_roles(custom_role)

    async def update_username_color(self, guild_id: int, user_id: int):
        guild: discord.Guild = self.bot.get_guild(guild_id)
        member: discord.Member = guild.get_member(user_id)

        custom_role_id = self.database.get_custom_role(guild_id, user_id)
        custom_color = self.database.get_custom_color(guild_id, user_id)

        if custom_color is None:
            return

        hex_value = int(custom_color, 16)

        color = discord.Color(hex_value)
        user_items = self.database.get_item_counts_by_user(guild_id, user_id)

        name_token_count = 0

        if ItemType.NAME_COLOR in user_items:
            name_token_count = user_items[ItemType.NAME_COLOR]

        if custom_role_id is None:
            if name_token_count <= 0:
                return
            custom_role = await self.create_custom_user_role(guild, member, color)
        else:
            custom_role = discord.utils.get(guild.roles, id=custom_role_id)

            if custom_role is None:
                if name_token_count <= 0:
                    return
                await self.create_custom_user_role(guild, member, color)
                return

            if name_token_count <= 0:
                await custom_role.delete(reason="Member ran out of name color tokens.")
                return

            if member.get_role(custom_role.id) is None:
                await member.add_roles(custom_role)

            await custom_role.edit(color=color)

    async def get_timeout_role(self, guild: discord.Guild) -> discord.Role:
        timeout_role = discord.utils.get(guild.roles, name=self.TIMEOUT_ROLE_NAME)

        if timeout_role is None:
            timeout_role = await self.reload_timeout_role(guild)

        return timeout_role

    async def reload_timeout_role(self, guild: discord.Guild) -> discord.Role:
        timeout_role = discord.utils.get(guild.roles, name=self.TIMEOUT_ROLE_NAME)

        if timeout_role is None:
            timeout_role = await guild.create_role(
                name=self.TIMEOUT_ROLE_NAME,
                mentionable=False,
                reason="Needed for server wide timeouts.",
            )

        bot_member = guild.get_member(self.bot.user.id)
        bot_roles = bot_member.roles

        max_pos = 0
        for role in bot_roles:
            max_pos = max(max_pos, role.position)

        max_pos = max_pos - 1

        await timeout_role.edit(position=max_pos)

        exclude_channels = self.settings.get_police_exclude_channels(guild.id)

        for channel in guild.channels:
            if channel.id in exclude_channels:
                continue

            bot_permissions = channel.permissions_for(bot_member)
            if not bot_permissions.manage_roles:
                self.logger.debug(
                    channel.guild.id,
                    f"Missing manage_roles permissions in {channel.name}.",
                    cog="Police",
                )
                continue

            role_overwrites = channel.overwrites_for(timeout_role)
            if role_overwrites.send_messages is False:
                continue
            role_overwrites.send_messages = False
            try:
                await channel.set_permissions(timeout_role, overwrite=role_overwrites)
            except discord.Forbidden:
                self.logger.debug(
                    channel.guild.id,
                    f"Missing permissions in {channel.name}.",
                    cog="Police",
                )

        return timeout_role
