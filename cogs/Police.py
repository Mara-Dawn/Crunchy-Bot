import asyncio
import datetime
import traceback
import discord

from discord.ext import commands
from discord import app_commands
from typing import Dict, Literal
from BotLogger import BotLogger
from BotSettings import BotSettings
from MaraBot import MaraBot
from cogs.Jail import Jail
from datalayer.Database import Database
from datalayer.PoliceList import PoliceList
from events.EventManager import EventManager
from events.JailEventType import JailEventType
from view.PoliceSettingsModal import PoliceSettingsModal

class Police(commands.Cog):
    
    TIMEOUT_ROLE_NAME = 'Timeout'
    
    def __init__(self, bot: MaraBot):
        self.bot = bot
        self.user_list: Dict[int, PoliceList] = {}
        self.logger: BotLogger = bot.logger
        self.settings: BotSettings = bot.settings
        self.event_manager: EventManager = bot.event_manager
        self.database: Database = bot.database
        
        self.initialized = False
    
    async def __has_permission(interaction: discord.Interaction) -> bool:
        author_id = 90043934247501824
        return interaction.user.id == author_id or interaction.user.guild_permissions.administrator
    
    async def __reload_timeout_role(self, guild: discord.Guild) -> discord.Role:
        timeout_role = discord.utils.get(guild.roles, name=self.TIMEOUT_ROLE_NAME)
        
        if timeout_role is None:
            timeout_role = await guild.create_role(
                name=self.TIMEOUT_ROLE_NAME,
                mentionable=False,
                reason="Needed for server wide timeouts."
            )
            
        bot_member = guild.get_member(self.bot.user.id)
        bot_roles = bot_member.roles
    
        max_pos = 0
        for role in bot_roles:
            max_pos = max(max_pos, role.position)
            
        max_pos = max_pos-1
        
        await timeout_role.edit(position=max_pos)
        
        exclude_channels = self.settings.get_police_exclude_channels(guild.id)
        
        for channel in guild.channels:
            if channel.id in exclude_channels:
                continue
            
            bot_permissions = channel.permissions_for(bot_member)
            if not bot_permissions.manage_roles:
                self.logger.debug(channel.guild.id, f'Missing manage_roles permissions in {channel.name}.', cog=self.__cog_name__)
                continue
            
            role_overwrites = channel.overwrites_for(timeout_role)
            if role_overwrites.send_messages is False:
                continue
            role_overwrites.send_messages = False
            try:
                await channel.set_permissions(timeout_role, overwrite=role_overwrites)
            except Exception as e:
                self.logger.debug(channel.guild.id, f'Missing permissions in {channel.name}.', cog=self.__cog_name__)
            
        return timeout_role
      
    async def __get_timeout_role(self, guild: discord.Guild) -> discord.Role:
        timeout_role = discord.utils.get(guild.roles, name=self.TIMEOUT_ROLE_NAME)

        if timeout_role is None:
            timeout_role = await self.__reload_timeout_role(guild)
                
        return timeout_role
    
    async def __jail_check(self, guild_id: int, user: discord.Member):
        timeout_count = self.database.get_timeout_tracker_count(guild_id, user.id)
        timeout_count_threshold = self.settings.get_police_timeouts_before_jail(guild_id)
        
        if timeout_count >= timeout_count_threshold:
            self.logger.log(guild_id, f'Timeout jail threshold reached for {user.name}', cog=self.__cog_name__)            
            jail_cog: Jail = self.bot.get_cog('Jail')
            duration = self.settings.get_police_timeout_jail_duration(guild_id)
            success = await jail_cog.jail_user(guild_id, self.bot.user.id, user, duration)
            timestamp_now = int(datetime.datetime.now().timestamp())
            release = timestamp_now + (duration*60)
            response = f'<@{user.id}> was timed out `{timeout_count}` times, resulting in a jail sentence.'
            if success:
                self.database.reset_timeout_tracker(guild_id, user.id)
                response += f' Their timeout count was reset and they will be released <t:{release}:R>.'
            else:
                affected_jails = self.database.get_active_jails_by_member(guild_id, user.id)
                
                if len(affected_jails) <= 0:
                    self.logger.error(guild_id, f'User already jailed but no active jail was found.', cog=self.__cog_name__)
                    return None
                
                jail_id = affected_jails[0].get_id()
                
                self.database.reset_timeout_tracker(guild_id, user.id)
                self.event_manager.dispatch_jail_event(datetime.datetime.now(), guild_id, JailEventType.INCREASE, self.bot.user.id, duration, jail_id)
                response += f' As they are already in jail, their sentence will be extended by `{duration}` minutes and their timeout count was reset.'
            
            return response
        return None
       
    async def timeout_task(self, channel: discord.TextChannel, user: discord.Member, duration: int):
        guild_id = channel.guild.id
        time_now = datetime.datetime.now()
        timestamp_now = int(time_now.timestamp())
        release = timestamp_now + duration
        
        naughty_list = self.user_list[guild_id]
        naughty_user = naughty_list.get_user(user.id)
        naughty_user.set_timeout_flag()
        
        self.event_manager.dispatch_timeout_event(time_now, guild_id, user.id, duration)
        
        try:
            timeout_role = await self.__get_timeout_role(channel.guild)
            await user.add_roles(timeout_role)
            
        except Exception as e:
            self.logger.log(channel.guild.id, f'Missing permissions to change user roles of {user.name}.', cog=self.__cog_name__)
            print(traceback.print_exc())
            
        await channel.send(f'<@{user.id}> {self.settings.get_police_timeout_notice(guild_id)} Try again <t:{release}:R>.', delete_after=(duration))
        self.logger.log(guild_id, f'Activated rate limit for {user.name}.', cog=self.__cog_name__)
            
        self.logger.log(channel.guild.id, f'Temporarily removed send_messages permission from {user.name}.', cog=self.__cog_name__)
        
        timeout_length = duration - (int(datetime.datetime.now().timestamp()) - timestamp_now)
        
        await asyncio.sleep(timeout_length)
        
        naughty_user.release()
        self.logger.log(guild_id, f'User {user.name} rate limit was reset.', cog=self.__cog_name__)
        
        try:
            timeout_role = await self.__get_timeout_role(channel.guild)
            await user.remove_roles(timeout_role)
            
        except Exception as e:
            self.logger.log(channel.guild.id, f'Missing permissions to change user roles of {user.name}.', cog=self.__cog_name__)
            print(traceback.print_exc())
            
        self.logger.log(guild_id, f'Reinstated old permissions for {user.name}.', cog=self.__cog_name__)
        
    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            self.user_list[guild.id] = PoliceList()
            
            timeout_role = await self.__get_timeout_role(guild)
            
            if len(timeout_role.members) > 0:
                self.logger.log("init","Ongoing timeouts found. Commencing cleanup.", cog=self.__cog_name__)
            
                for member in timeout_role.members:
                    await member.remove_roles(timeout_role)
                    self.logger.log("init",f"Removed Timeout role from {member.display_name}.", cog=self.__cog_name__)
        
        self.logger.log("init",str(self.__cog_name__) + " loaded.", cog=self.__cog_name__)
        self.initialized = True

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        if not self.initialized:
           return
        self.user_list[guild.id] = PoliceList()
        
        await self.__reload_timeout_role(guild)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        if not self.initialized:
           return
        del self.user_list[guild.id]

    @commands.Cog.listener()
    async def on_message(self, message: discord.message.Message):
        if not self.initialized:
           return
       
        author_id = message.author.id
        if author_id == self.bot.user.id:
            return
        
        if message.author.bot:
            return
        
        if len(message.content) > 0 and message.content[0] == "/":
            return
        
        if not message.guild:
            return
        
        guild_id = message.guild.id
        
        if not self.settings.get_police_enabled(guild_id):
            return 
        
        user_list = self.user_list[guild_id]
        
        message_limit = self.settings.get_police_message_limit(guild_id)
        message_limit_interval = self.settings.get_police_message_limit_interval(guild_id)
            
        if not user_list.has_user(author_id):
            self.logger.log(guild_id, f'Added rate tracking for user {message.author.name}', cog=self.__cog_name__)
            user_list.add_user(author_id)
            
        user_node = user_list.get_user(author_id)
        
        user_list.track_spam_message(author_id, message.created_at)
        
        if user_node.spam_check(message_limit_interval, message_limit):
            if user_node.check_spam_score_increase(message_limit_interval, message_limit):
                self.event_manager.dispatch_spam_event(datetime.datetime.now(), guild_id, author_id)
                self.logger.log(guild_id, f'Spam counter increased for {message.author.name}', cog=self.__cog_name__)
        
        if bool(set([x.id for x in message.author.roles]).intersection(self.settings.get_police_naughty_roles(guild_id))):
            self.logger.debug(guild_id, f'{message.author.name} has matching roles', cog=self.__cog_name__)
            
            if user_node.is_in_timeout() or message.channel.id in self.settings.get_police_exclude_channels(guild_id):
                return
            
            user_list.track_timeout_message(author_id, message.created_at)
            
            if user_node.timeout_check(message_limit_interval, message_limit):
                self.database.increment_timeout_tracker(guild_id, author_id)
                
                response = await self.__jail_check(guild_id, message.author)
                
                if response is not None:
                    await message.channel.send(response)
                else:
                    duration = self.settings.get_police_timeout(guild_id)
                    self.bot.loop.create_task(self.timeout_task(message.channel, message.author, duration))
                
        elif user_list.has_user(author_id):
            self.logger.log(guild_id, f'Removed rate tracking for user {message.author.name}', cog=self.__cog_name__)
            user_list.remove_user(author_id)

    group = app_commands.Group(name="police", description="Subcommands for the Police module.")

    @app_commands.command(name="meow", description="Makes me meow!")
    async def meow(self, interaction: discord.Interaction) -> None:
        await self.bot.command_response(self.__cog_name__, interaction, "Meow!")
        
    @group.command(name="settings", description="Overview of all police related settings and their current value.")
    @app_commands.check(__has_permission)
    async def get_settings(self, interaction: discord.Interaction):
        output = self.settings.get_settings_string(interaction.guild_id, BotSettings.POLICE_SUBSETTINGS_KEY)
        await self.bot.command_response(self.__cog_name__, interaction, output)
    
    @app_commands.command(name="timeout", description='Timeout a user.')
    @app_commands.describe(
        user='User who will be timed out.',
        duration='Length of the timeout. (in seconds)'
        )
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def timeout(self, interaction: discord.Interaction, user: discord.Member, duration: app_commands.Range[int, 1]):
        naughty_list = self.user_list[interaction.guild_id]
        
        if naughty_list.has_user(user.id) and naughty_list.get_user(user.id).is_in_timeout():
            await self.bot.command_response(self.__cog_name__, interaction, "User already in timeout.")
        
        if not naughty_list.has_user(user.id):
                message_limit = self.settings.get_police_message_limit(interaction.guild_id)
                self.logger.log(interaction.guild_id, f'Added rate tracking for user {user.name}', cog=self.__cog_name__)
                naughty_list.add_user(user.id, message_limit)
        
        self.bot.loop.create_task(self.timeout_task(interaction.channel, user, duration))
        await self.bot.command_response(self.__cog_name__, interaction, "User timed out successfully.", user.name, duration)
    
    @group.command(name="toggle", description="Enable or disable the entire police module.")
    @app_commands.describe(enabled='Turns the police module on or off.')
    @app_commands.check(__has_permission)
    async def set_toggle(self, interaction: discord.Interaction, enabled: Literal['on', 'off']):
        self.settings.set_police_enabled(interaction.guild_id, enabled == "on")
        await self.bot.command_response(self.__cog_name__, interaction, f'Police module was turned {enabled}.', enabled)
    
    @group.command(name="add_role", description="Add roles to be monitored by spam detection.")
    @app_commands.describe(role='The role that shall be tracked for spam detection.')
    @app_commands.check(__has_permission)
    async def add_role(self, interaction: discord.Interaction, role: discord.Role):
        self.settings.add_police_naughty_role(interaction.guild_id, role.id)
        await self.bot.command_response(self.__cog_name__, interaction, f'Added {role.name} to the list of active roles.', role)
        
    @group.command(name="remove_role", description="Remove roles from spam detection.")
    @app_commands.describe(role='Remove spam detection from this role.')
    @app_commands.check(__has_permission)
    async def remove_role(self, interaction: discord.Interaction, role: discord.Role):
        self.settings.remove_police_naughty_role(interaction.guild_id, role.id)
        await self.bot.command_response(self.__cog_name__, interaction, f'Removed {role.name} from active roles.', role)
    
    @group.command(name="untrack_channel", description="Stop tracking spam in specific channels.")
    @app_commands.describe(channel='Stop tracking spam for this channel.')
    @app_commands.check(__has_permission)
    async def untrack_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await interaction.response.defer(ephemeral=True)
        self.settings.add_police_exclude_channel(interaction.guild_id, channel.id)
        await self.__reload_timeout_role(interaction.guild)
        await self.bot.command_response(self.__cog_name__, interaction, f'Stopping spam detection in {channel.name}.', channel)
        
    @group.command(name="track_channel", description='Reenable tracking spam for specific channels.')
    @app_commands.describe(channel='Reenable tracking spam for this channel.')
    @app_commands.check(__has_permission)
    async def track_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await interaction.response.defer(ephemeral=True)
        self.settings.remove_police_exclude_channel(interaction.guild_id, channel.id)
        await self.__reload_timeout_role(interaction.guild)
        await self.bot.command_response(self.__cog_name__, interaction, f'Resuming spam detection in {channel.name}.', channel)
    
    @group.command(name="setup", description="Opens a dialog to edit various police settings.")
    @app_commands.check(__has_permission)
    async def setup(self, interaction: discord.Interaction):
        current_timeout = self.settings.get_police_timeout(interaction.guild_id)
        current_message_limit = self.settings.get_police_message_limit(interaction.guild_id)
        current_message_limit_interval = self.settings.get_police_message_limit_interval(interaction.guild_id)
        current_timeouts_before_jail = self.settings.get_police_timeouts_before_jail(interaction.guild_id)
        current_timeout_jail_duration = self.settings.get_police_timeout_jail_duration(interaction.guild_id)

        modal = PoliceSettingsModal(self.bot, self.settings)
        modal.timeout_length.default = current_timeout
        modal.message_limit.default = current_message_limit
        modal.message_limit_interval.default = current_message_limit_interval
        modal.timeouts_before_jail.default = current_timeouts_before_jail
        modal.timeout_jail_duration.default = current_timeout_jail_duration
        
        await interaction.response.send_modal(modal)
    
    @group.command(name="set_timeout_message")
    @app_commands.describe(message='This will be sent to the timed out person.')
    @app_commands.check(__has_permission)
    async def set_message(self, interaction: discord.Interaction, message: str):

        self.settings.set_police_timeout_notice(interaction.guild_id, message)
        await self.bot.command_response(self.__cog_name__, interaction, f'Timeout warning set to:\n `{message}`', message)
    
async def setup(bot):
    await bot.add_cog(Police(bot))
