import datetime

import discord
from bot_util import BotUtil
from datalayer.database import Database
from datalayer.jail import UserJail
from discord.ext import commands
from events.bot_event import BotEvent
from events.jail_event import JailEvent
from events.types import JailEventType

# needed for global access
from items import *  # noqa: F403

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
        pass

    def get_jail_duration(self, jail: UserJail) -> int:
        events = self.database.get_jail_events_by_jail(jail.id)
        total_duration = 0
        for event in events:
            total_duration += event.duration

        return total_duration

    def get_jail_remaining(self, jail: UserJail) -> float:
        duration = self.get_jail_duration(jail)
        release_timestamp = jail.jailed_on + datetime.timedelta(minutes=duration)
        remainder = release_timestamp - datetime.datetime.now()
        return max(remainder.total_seconds() / 60, 0)
    
    async def announce(self, guild: discord.Guild, message: str, *args, **kwargs) -> str:
        jail_channels = self.settings_manager.get_jail_channels(guild.id)
        
        for channel_id in jail_channels:
            channel = guild.get_channel(channel_id)
            await channel.send(message, *args, **kwargs)

    async def jail_user(self, guild_id: int, jailed_by_id: int, user: discord.Member, duration: int) -> bool:
        active_jails = self.database.get_active_jails_by_guild(guild_id)
        jailed_members = [jail.member_id for jail in active_jails]
        
        jail_role = self.settings_manager.get_jail_role(guild_id)
        
        if user.id in jailed_members or user.get_role(jail_role) is not None:
            return False
        
        await user.add_roles(self.bot.get_guild(guild_id).get_role(jail_role))
        
        time_now = datetime.datetime.now()
        jail = UserJail(guild_id, user.id, time_now)
        
        jail = self.database.log_jail_sentence(jail)
        
        time_now = datetime.datetime.now()
        event = JailEvent(time_now, guild_id, JailEventType.JAIL, jailed_by_id, duration, jail.id)
        await self.controller.dispatch_event(event)
        
        return True
    
    async def release_user(self, guild_id: int, released_by_id: int, user: discord.Member) -> str:
        active_jails = self.database.get_active_jails_by_guild(guild_id)
        jailed_members = [jail.member_id for jail in active_jails]
        
        jail_role = self.settings_manager.get_jail_role(guild_id)
        
        if user.id not in jailed_members or user.get_role(jail_role) is None:
            return False
        
        
        await user.remove_roles(user.get_role(jail_role))
        
        affected_jails = self.database.get_active_jails_by_member(guild_id, user.id)
                
        if len(affected_jails) > 0:
            jail = affected_jails[0]
            remaining = self.get_jail_remaining(jail)
            response = f'Their remaining sentence of `{BotUtil.strfdelta(remaining, inputtype='minutes')}` will be forgiven.'

            time_now = datetime.datetime.now()
            event = JailEvent(time_now, guild_id, JailEventType.RELEASE, released_by_id, 0, jail.id)
            await self.controller.dispatch_event(event)
            
        return response
