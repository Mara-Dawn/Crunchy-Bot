import asyncio
import copy
import datetime
import traceback
import discord

from discord.ext import commands
from discord import Message, app_commands
from typing import Dict, Literal, Optional
from BotLogger import BotLogger
from BotSettings import BotSettings
from MaraBot import MaraBot
from datalayer.PoliceList import PoliceList
from datalayer.PoliceListNode import PoliceListNode
from events.BotEventManager import BotEventManager
from view.PoliceSettingsModal import PoliceSettingsModal

class Police(commands.Cog):
    
    def __init__(self, bot: MaraBot):
        self.bot = bot
        self.naughty_list: Dict[int, PoliceList] = {}
        self.logger: BotLogger = bot.logger
        self.settings: BotSettings = bot.settings
        self.event_manager: BotEventManager = bot.event_manager
        
        self.initialized = False
    
    async def __has_permission(interaction: discord.Interaction) -> bool:
        
        author_id = 90043934247501824
        return interaction.user.id == author_id or interaction.user.guild_permissions.administrator
    
    async def timeout_task(self, channel: discord.TextChannel, user: discord.Member, duration: int):
        
        guild_id = channel.guild.id
        
        time_now = datetime.datetime.now()
        timestamp_now = int(time_now.timestamp())
        release = timestamp_now + duration
        
        naughty_list = self.naughty_list[guild_id]
        naughty_user = naughty_list.get_user(user.id)
        
        naughty_user.timeout()
        
        user_overwrites = channel.overwrites_for(user)
        initial_overwrites = copy.deepcopy(user_overwrites)
        user_overwrites.send_messages = False
        
        self.event_manager.dispatch_timeout_event(time_now, guild_id, user.id, duration)
        
        try:
            await channel.set_permissions(user, overwrite=user_overwrites)
            
        except Exception as e:
            self.logger.log(channel.guild.id, f'Missing permissions to change user permissions in {channel.name}.', cog=self.__cog_name__)
            print(traceback.print_exc())
            
        await channel.send(f'<@{user.id}> {self.settings.get_police_timeout_notice(guild_id)} Try again <t:{release}:R>.', delete_after=(duration))
        self.logger.log(guild_id, f'Activated rate limit for {user.name} in {channel.name}.', cog=self.__cog_name__)
            
        self.logger.log(channel.guild.id, f'Temporarily removed send_messages permission from {user.name} in {channel.name}.', cog=self.__cog_name__)
        
        timeout_length = duration - (int(datetime.datetime.now().timestamp()) - timestamp_now)
        
        await asyncio.sleep(timeout_length)
        
        naughty_user.release()
        self.logger.log(guild_id, f'User {user.name} rate limit was reset.', cog=self.__cog_name__)
        
        try:
            await channel.set_permissions(user, overwrite=initial_overwrites)
            
        except Exception as e:
            self.logger.log(channel.guild.id, f'Missing permissions to change user permissions in {channel.name}.', cog=self.__cog_name__)
            print(traceback.print_exc())
            
        
        self.logger.log(guild_id, f'Reinstated old permissions for {user.name} in {channel.name}.', cog=self.__cog_name__)
        
    @commands.Cog.listener()
    async def on_ready(self):

        for guild in self.bot.guilds:
            self.naughty_list[guild.id] = PoliceList()
            
        self.logger.log("init",str(self.__cog_name__) + " loaded.", cog=self.__cog_name__)
        
        self.initialized = True

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        
        if not self.initialized:
           return
       
        self.naughty_list[guild.id] = PoliceList()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        
        if not self.initialized:
           return
       
        del self.naughty_list[guild.id]

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
        
        if message.channel.id in self.settings.get_police_exclude_channels(guild_id):
            return
        
        naughty_list = self.naughty_list[guild_id]
        
        if bool(set([x.id for x in message.author.roles]).intersection(self.settings.get_police_naughty_roles(guild_id))):

            self.logger.debug(guild_id, f'{message.author.name} has matching roles', cog=self.__cog_name__)
            
            if not naughty_list.has_user(author_id):
                
                message_limit = self.settings.get_police_message_limit(guild_id)
                self.logger.log(guild_id, f'Added rate tracking for user {message.author.name}', cog=self.__cog_name__)
                naughty_list.add_user(author_id, message_limit)
                naughty_list.add_message(author_id, message.created_at)
                return
            
            naughty_list.add_message(author_id, message.created_at)
            
            message_limit_interval = self.settings.get_police_message_limit_interval(guild_id)
            naughty_user = naughty_list.get_user(author_id)
            
            if not naughty_user.is_in_timeout():
                
                if not naughty_user.is_spamming(message_limit_interval):
                    return
                
                duration = self.settings.get_police_timeout(guild_id)
                self.bot.loop.create_task(self.timeout_task(message.channel, message.author, duration))
                
        elif naughty_list.has_user(author_id):
            
            self.logger.log(guild_id, f'Removed rate tracing for user {message.author.name}', cog=self.__cog_name__)
            naughty_list.remove_user(author_id)

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
        
        naughty_list = self.naughty_list[interaction.guild_id]
        
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
        
        self.settings.add_police_exclude_channel(interaction.guild_id, channel.id)
        await self.bot.command_response(self.__cog_name__, interaction, f'Stopping spam detection in {channel.name}.', channel)
        
    @group.command(name="track_channel", description='Reenable tracking spam for specific channels.')
    @app_commands.describe(channel='Reenable tracking spam for this channel.')
    @app_commands.check(__has_permission)
    async def track_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        
        self.settings.remove_police_exclude_channel(interaction.guild_id, channel.id)
        await self.bot.command_response(self.__cog_name__, interaction, f'Resuming spam detection in {channel.name}.', channel)
    
    @group.command(name="setup", description="Opens a dialog to edit various police settings.")
    @app_commands.check(__has_permission)
    async def setup(self, interaction: discord.Interaction):
        
        current_timeout = self.settings.get_police_timeout(interaction.guild_id)
        current_message_limit = self.settings.get_police_message_limit(interaction.guild_id)
        current_message_limit_interval = self.settings.get_police_message_limit_interval(interaction.guild_id)
        current_timeout_notice = self.settings.get_police_timeout_notice(interaction.guild_id)

        modal = PoliceSettingsModal(self.bot, self.settings)
        modal.timeout_length.default = current_timeout
        modal.message_limit.default = current_message_limit
        modal.message_limit_interval.default = current_message_limit_interval
        modal.timeout_notice.default = current_timeout_notice
        
        await interaction.response.send_modal(modal)
        
async def setup(bot):
    await bot.add_cog(Police(bot))
