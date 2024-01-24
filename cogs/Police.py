import asyncio
import copy
import datetime
import traceback
import discord

from discord.ext import commands
from discord import Message
from discord.commands import SlashCommandGroup
from discord.commands import SlashCommand
from typing import Dict, Literal, Optional
from BotLogger import BotLogger
from BotSettings import BotSettings
from MaraBot import MaraBot
from datalayer.PoliceList import PoliceList
from datalayer.PoliceListNode import PoliceListNode
from events.BotEventManager import BotEventManager

class Police(commands.Cog):
    
    def __init__(self, bot: MaraBot):
        self.bot = bot
        
        self.naughty_list: Dict[int, PoliceList] = {}
        self.logger: BotLogger = bot.logger
        self.settings: BotSettings = bot.settings
        self.event_manager: BotEventManager = bot.event_manager
    
    async def __has_permission(self, ctx: discord.ApplicationContext) -> bool:
        
        author_id = 90043934247501824
        return ctx.author.id == author_id or ctx.author.guild_permissions.administrator
    
    async def timeout_task(self, message: Message, user_node: PoliceListNode):
        
        channel = message.channel
        user = message.author
        guild_id = message.guild.id
        timeout_max = self.settings.get_police_timeout(guild_id)
        
        time_now = datetime.datetime.now()
        timestamp_now = int(time_now.timestamp())
        release = timestamp_now + timeout_max
        user_node.timeout()
        
        user_overwrites = channel.overwrites_for(user)
        initial_overwrites = copy.deepcopy(user_overwrites)
        user_overwrites.send_messages = False
        
        self.event_manager.dispatch_timeout_event(time_now, guild_id, user.id, timeout_max)
        
        try:
            await channel.set_permissions(user, overwrite=user_overwrites)
            
        except Exception as e:
            self.logger.log(channel.guild.id, f'Missing permissions to change user permissions in {channel.name}.', cog=self.__cog_name__)
            print(traceback.print_exc())
            
        await message.channel.send(f'<@{user.id}> {self.settings.get_police_timeout_notice(guild_id)} Try again <t:{release}:R>.', delete_after=(timeout_max))
        self.logger.log(guild_id, f'Activated rate limit for {message.author.name} in {channel.name}.', cog=self.__cog_name__)
        await message.delete()
            
        self.logger.log(channel.guild.id, f'Temporarily removed send_messages permission from {user.name} in {channel.name}.', cog=self.__cog_name__)
        
        timeout_length = timeout_max - (int(datetime.datetime.now().timestamp()) - timestamp_now)
        
        await asyncio.sleep(timeout_length)
        
        user_node.release()
        self.logger.log(guild_id, f'User {message.author.name} rate limit was reset.', cog=self.__cog_name__)
        
        try:
            await channel.set_permissions(message.author, overwrite=initial_overwrites)
            
        except Exception as e:
            self.logger.log(channel.guild.id, f'Missing permissions to change user permissions in {channel.name}.', cog=self.__cog_name__)
            print(traceback.print_exc())
            
        
        self.logger.log(guild_id, f'Reinstated old permissions for {user.name} in {channel.name}.', cog=self.__cog_name__)
        
    @commands.Cog.listener()
    async def on_ready(self):

        for guild in self.bot.guilds:
            self.naughty_list[guild.id] = PoliceList()
            
        self.logger.log("init",str(self.__cog_name__) + " loaded.", cog=self.__cog_name__)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):

        self.naughty_list[guild.id] = PoliceList()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):

        del self.naughty_list[guild.id]

    @commands.Cog.listener()
    async def on_message(self, message: discord.message.Message):
       
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
                self.logger.log(guild_id, f'Added rate tracking for user {message.author.name}')
                naughty_list.add_user(author_id, message_limit)
                naughty_list.add_message(author_id, message.created_at)
                return
            
            naughty_list.add_message(author_id, message.created_at)
            
            message_limit_interval = self.settings.get_police_message_limit_interval(guild_id)
            naughty_user = naughty_list.get_user(author_id)
            
            if not naughty_user.is_in_timeout():
                
                if not naughty_user.is_spamming(message_limit_interval):
                    return
                
                self.bot.loop.create_task(self.timeout_task(message, naughty_user))
                
        elif naughty_list.has_user(author_id):
            
            self.logger.log(guild_id, f'Removed rate tracing for user {message.author.name}', cog=self.__cog_name__)
            naughty_list.remove_user(author_id)

    @discord.slash_command(name="meow", description="Makes me meow back at you.")
    @discord.guild_only()
    async def meow(self, ctx: discord.ApplicationContext) -> None:
        
        await self.bot.command_response(self.__cog_name__, ctx, "Meow!")
    
    police = SlashCommandGroup(name="police", description="Subcommands for the Police module.")

    @police.command(name="settings", description="Overview of all police related settings and their current value.")
    @discord.guild_only()
    async def get_settings(self, ctx: discord.ApplicationContext):
        
        if not self.__has_permission(ctx):
            raise commands.MissingPermissions
        
        output = self.settings.get_settings_string(ctx.guild_id, BotSettings.POLICE_SUBSETTINGS_KEY)
        
        await self.bot.command_response(self.__cog_name__, ctx, output)
    
    
    @police.command(name="toggle", description="Enable or disable the entire police module.")
    @discord.option(
        "enabled",
        description="Enable or disable the entire police module.",
        choices=['on', 'off']
    )
    @discord.guild_only()
    async def set_toggle(self, ctx: discord.ApplicationContext, enabled: str):
        
        if not self.__has_permission(ctx):
            raise commands.MissingPermissions
        
        self.settings.set_police_enabled(ctx.guild_id, enabled == "on")
        
        await self.bot.command_response(self.__cog_name__, ctx, f'Police module was turned {enabled}.', enabled)
    
    @police.command(name="set_timeout_length", description="Specify the length of time a user will be timed out when he spams.")
    @discord.option(
        "length",
        type=int,
        description="Timeout length (in seconds)",
        min_value=1
    )
    @discord.guild_only()
    async def set_timeout_interval(self, ctx: discord.ApplicationContext, length: int):
        
        if not self.__has_permission(ctx):
            raise commands.MissingPermissions
        
        self.settings.set_police_timeout(ctx.guild_id, length)
        await self.bot.command_response(self.__cog_name__, ctx, f'Timeout length set to {length} seconds.', length)
    
    
    @police.command(name="set_spam_thresholds", description="Specify the length of time a user will be timed out when he spams.")
    @discord.option(
        "message_count",
        type=int,
        description='Numer of messages a user may send within the specified interval.',
        min_value=1
    )
    @discord.option(
        "interval",
        type=int,
        description='Time interval within the user is allowed to send message_count messages.  (in seconds)',
        min_value=1
    )
    @discord.guild_only()
    async def set_spam_thresholds(self, ctx: discord.ApplicationContext, message_count: int, interval: int):
        
        if not self.__has_permission(ctx):
            raise commands.MissingPermissions
        
        self.settings.set_police_message_limit(ctx.guild_id, message_count)
        self.settings.set_police_message_limit_interval(ctx.guild_id, interval)
        
        for guild_id in self.naughty_list:
            self.naughty_list[guild_id].clear()
        
        await self.bot.command_response(self.__cog_name__, ctx, f'Rate limit updated: Users can send {message_count} messages within {interval} seconds before getting timed out.', message_count, interval)
    
    @police.command(name="add_role", description="Add roles to be monitored by spam detection.")
    @discord.option(
        "role",
        type=discord.Role,
        description='The role that shall be tracked for spam detection.'
    )
    @discord.guild_only()
    async def add_role(self, ctx: discord.ApplicationContext, role: discord.Role):
        
        if not self.__has_permission(ctx):
            raise commands.MissingPermissions
        
        self.settings.add_police_naughty_role(ctx.guild_id, role.id)
        await self.bot.command_response(self.__cog_name__, ctx, f'Added {role.name} to the list of active roles.', role)
        
    @police.command(name="remove_role", description="Remove roles from spam detection.")
    @discord.option(
        "role",
        type=discord.Role,
        description='Remove spam detection from this role.'
    )
    @discord.guild_only()
    async def remove_role(self, ctx: discord.ApplicationContext, role: discord.Role):
        
        if not self.__has_permission(ctx):
            raise commands.MissingPermissions
        
        self.settings.remove_police_naughty_role(ctx.guild_id, role.id)
        await self.bot.command_response(self.__cog_name__, ctx, f'Removed {role.name} from active roles.', role)
    
    @police.command(name="untrack_channel", description="Stop tracking spam in specific channels.")
    @discord.option(
        "channel",
        type=discord.TextChannel,
        description='Stop tracking spam for this channel.'
    )
    @discord.guild_only()
    async def untrack_channel(self, ctx: discord.ApplicationContext, channel: discord.TextChannel):
        
        if not self.__has_permission(ctx):
            raise commands.MissingPermissions
        
        self.settings.add_police_exclude_channel(ctx.guild_id, channel.id)
        await self.bot.command_response(self.__cog_name__, ctxctx, f'Stopping spam detection in {channel.name}.', channel)
        
    @police.command(name="track_channel", description='Reenable tracking spam for specific channels.')
    @discord.option(
        "channel",
        type=discord.TextChannel,
        description='Reenable tracking spam for this channel.'
    )
    @discord.guild_only()
    async def track_channel(self, ctx: discord.ApplicationContext, channel: discord.TextChannel):
        
        if not self.__has_permission(ctx):
            raise commands.MissingPermissions
        
        self.settings.remove_police_exclude_channel(ctx.guild_id, channel.id)
        await self.bot.command_response(self.__cog_name__, ctx, f'Resuming spam detection in {channel.name}.', channel)
    
    @police.command(name="set_timeout_message", description='Set the message a user will recieve when timed out.')
    @discord.option(
        "message",
        description='This will be sent to the timed out person.'
    )
    @discord.guild_only()
    async def set_message(self, interaction: discord.Interaction, message: str):
        
        self.settings.set_police_timeout_notice(interaction.guild_id, message)
        await self.bot.command_response(self.__cog_name__, interaction, f'Timeout warning set to:\n `{message}`', message)
                
def setup(bot):
    bot.add_cog(Police(bot))
