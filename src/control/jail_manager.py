import datetime
import random

import discord
from bot_util import BotUtil
from datalayer.database import Database
from datalayer.jail import UserJail
from discord.ext import commands
from events.bot_event import BotEvent
from events.inventory_event import InventoryEvent
from events.jail_event import JailEvent
from events.types import EventType, JailEventType

# needed for global access
from items import *  # noqa: F403
from items.types import ItemType

from control.controller import Controller
from control.logger import BotLogger
from control.service import Service
from control.settings_manager import SettingsManager


class JailManager(Service):

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
        self.log_name = "Jail"

    async def listen_for_event(self, event: BotEvent):
        match event.type:
            case EventType.INVENTORY:
                inventory_event: InventoryEvent = event
                match inventory_event.item_type:
                    case ItemType.EXPLOSIVE_FART:
                        if inventory_event.amount <= 0:
                            guild = self.bot.get_guild(event.guild_id)
                            await self.random_jailing(guild, event.get_causing_user_id())

    async def get_active_jail(self, guild_id: int, user: discord.Member) -> UserJail:
        affected_jails = await self.database.get_active_jails_by_member(guild_id, user.id)
        
        jail_role = await self.settings_manager.get_jail_role(guild_id)
        
        if not(len(affected_jails) > 0 and user.get_role(jail_role) is not None):
            return None
        
        return affected_jails[0]

    async def get_jail_duration(self, jail: UserJail) -> int:
        events = await self.database.get_jail_events_by_jail(jail.id)
        total_duration = 0
        for event in events:
            total_duration += event.duration

        return total_duration

    async def get_jail_remaining(self, jail: UserJail) -> float:
        duration = await self.get_jail_duration(jail)
        release_timestamp = jail.jailed_on + datetime.timedelta(minutes=duration)
        remainder = release_timestamp - datetime.datetime.now()
        return max(remainder.total_seconds() / 60, 0)
    
    async def announce(self, guild: discord.Guild, message: str, *args, **kwargs) -> str:
        jail_channels = await self.settings_manager.get_jail_channels(guild.id)
        
        for channel_id in jail_channels:
            channel = guild.get_channel(channel_id)
            await channel.send(message, *args, **kwargs)

    async def jail_user(self, guild_id: int, jailed_by_id: int, user: discord.Member, duration: int) -> bool:
        active_jails = await self.database.get_active_jails_by_guild(guild_id)
        jailed_members = [jail.member_id for jail in active_jails]
        
        jail_role = await self.settings_manager.get_jail_role(guild_id)
        
        if user.id in jailed_members or user.get_role(jail_role) is not None:
            return False
        
        await user.add_roles(self.bot.get_guild(guild_id).get_role(jail_role))
        
        time_now = datetime.datetime.now()
        jail = UserJail(guild_id, user.id, time_now)
        
        jail = await self.database.log_jail_sentence(jail)
        
        time_now = datetime.datetime.now()
        event = JailEvent(time_now, guild_id, JailEventType.JAIL, jailed_by_id, duration, jail.id)
        await self.controller.dispatch_event(event)
        
        return True
    
    async def release_user(self, guild_id: int, released_by_id: int, user: discord.Member) -> str:
        active_jails = await self.database.get_active_jails_by_guild(guild_id)
        jailed_members = [jail.member_id for jail in active_jails]
        
        jail_role = await self.settings_manager.get_jail_role(guild_id)
        
        if user.id not in jailed_members or user.get_role(jail_role) is None:
            return False
        
        
        await user.remove_roles(user.get_role(jail_role))
        
        affected_jails = await self.database.get_active_jails_by_member(guild_id, user.id)
                
        if len(affected_jails) > 0:
            jail = affected_jails[0]
            remaining = await self.get_jail_remaining(jail)
            response = f'Their remaining sentence of `{BotUtil.strfdelta(remaining, inputtype='minutes')}` will be forgiven.'

            time_now = datetime.datetime.now()
            event = JailEvent(time_now, guild_id, JailEventType.RELEASE, released_by_id, 0, jail.id)
            await self.controller.dispatch_event(event)
            
        return response
    
    async def random_jailing(self, guild: discord.Guild, member_id: int):
        guild_id = guild.id
        bean_data = await self.database.get_guild_beans(guild_id)
        users = []

        for user_id, amount in bean_data.items():
            if amount >= 100:
                users.append(user_id)

        jails = await self.database.get_active_jails_by_guild(guild_id)

        for jail in jails:
            jailed_member_id = jail.member_id
            if jailed_member_id in users:
                users.remove(jailed_member_id)

        victims = random.sample(users, min(5, len(users)))

        jail_announcement = f"After committing unspeakable atrocities, <@{member_id}> caused innocent bystanders to be banished into the abyss."
        await self.announce(guild, jail_announcement)

        for victim in victims:
            duration = random.randint(5 * 60, 10 * 60)
            member = guild.get_member(victim)

            if member is None:
                continue

            success = await self.jail_user(
                guild_id, member_id, member, duration
            )

            if not success:
                continue

            timestamp_now = int(datetime.datetime.now().timestamp())
            release = timestamp_now + (duration * 60)
            jail_announcement = f"<@{victim}> was sentenced to Jail. They will be released <t:{release}:R>."
            await self.announce(guild, jail_announcement)
