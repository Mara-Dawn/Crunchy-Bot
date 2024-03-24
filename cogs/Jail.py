import datetime
import random
import discord

from discord.ext import tasks, commands
from discord import app_commands
from typing import Literal
from BotLogger import BotLogger
from BotSettings import BotSettings
from BotUtil import BotUtil
from MaraBot import MaraBot
from datalayer.Database import Database
from datalayer.UserJail import UserJail
from datalayer.UserInteraction import UserInteraction
from events.EventManager import EventManager
from events.JailEventType import JailEventType
from view.JailSettingsModal import JailSettingsModal

class Jail(commands.Cog):
    
    def __init__(self, bot: MaraBot):
        self.bot = bot
        self.logger: BotLogger = bot.logger
        self.settings: BotSettings = bot.settings
        self.database: Database = bot.database
        self.event_manager: EventManager = bot.event_manager

    
    async def __has_permission(interaction: discord.Interaction) -> bool:
        author_id = 90043934247501824
        return interaction.user.id == author_id or interaction.user.guild_permissions.administrator
    
    def __has_mod_permission(self, interaction: discord.Interaction) -> bool:
        author_id = 90043934247501824
        roles = self.settings.get_jail_mod_roles(interaction.guild_id)
        is_mod = len(set([x.id for x in interaction.user.roles]).intersection(roles)) > 0
        return interaction.user.id == author_id or interaction.user.guild_permissions.administrator or is_mod
    
    async def __check_enabled(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        if not self.settings.get_jail_enabled(guild_id):
            await self.bot.command_response(self.__cog_name__, interaction, f'Jail module is currently disabled.')
            return False
        return True
    
    def __get_already_used_msg(self, type: UserInteraction, interaction: discord.Interaction, user: discord.Member) -> str:
        match type:
            case UserInteraction.SLAP:
                return f'<@{user.id}> was slapped by <@{interaction.user.id}>!\n You already slapped {user.display_name}, no extra time will be added this time.'
            case UserInteraction.PET:
                return f'<@{user.id}> recieved pets from <@{interaction.user.id}>!\n You already gave {user.display_name} pets, no extra time will be added this time.'
            case UserInteraction.FART:
                return f'<@{user.id}> was farted on by <@{interaction.user.id}>!\n{user.display_name} already enjoyed your farts, no extra time will be added this time.'
            
    def __get_already_used_log_msg(self, type: UserInteraction, interaction: discord.Interaction, user: discord.Member) -> str:
        match type:
            case UserInteraction.SLAP:
                return f'User {user.display_name} was already slapped by {interaction.user.display_name}. No extra time will be added.'
            case UserInteraction.PET:
                return f'User {user.display_name} already recieved pats from {interaction.user.display_name}. No extra time will be added.'
            case UserInteraction.FART:
                return f'User {user.display_name} already enjoyed {interaction.user.display_name}\'s farts. No extra time will be added.'
 
    async def user_command_interaction(self, interaction: discord.Interaction, user: discord.Member, command_type: UserInteraction) -> str:
        command = interaction.command
        guild_id = interaction.guild_id
        
        affected_jails = self.database.get_active_jails_by_member(guild_id, user.id)
        
        jail_role = self.settings.get_jail_role(guild_id)
        jail_channels = self.settings.get_jail_channels(guild_id)
        
        if not(len(affected_jails) > 0 and user.get_role(jail_role) is not None and interaction.channel_id in jail_channels):
            return ''
        
        affected_jail = affected_jails[0]
        
        self.logger.debug(guild_id, f'{command.name}: targeted user {user.name} is in jail.', cog=self.__cog_name__)
        
        if self.event_manager.has_jail_event_from_user(affected_jail.get_id(), interaction.user.id, command.name) and not self.__has_mod_permission(interaction):
            self.logger.log(guild_id, self.__get_already_used_log_msg(command_type, interaction, user), cog=self.__cog_name__)
            return self.__get_already_used_msg(command_type, interaction, user)

        response = '\n'
        amount = 0
        
        match command_type:
            case UserInteraction.SLAP:
                amount = self.settings.get_jail_slap_time(interaction.guild_id)
            case UserInteraction.PET:
                amount = -self.settings.get_jail_pet_time(interaction.guild_id)
            case UserInteraction.FART:
                min_amount = self.settings.get_jail_fart_min(interaction.guild_id)
                max_amount = self.settings.get_jail_fart_max(interaction.guild_id)
                amount = random.randint(min_amount, max_amount)
        
        remaining = self.event_manager.get_jail_remaining(affected_jail)
        amount = max(amount, -int(remaining+1))
        
        crit_mod = self.settings.get_jail_base_crit_mod(interaction.guild_id)
        crit_rate = self.settings.get_jail_base_crit_rate(interaction.guild_id)
        
        is_crit = random.random() <= crit_rate
        
        if is_crit:
            response += f'**CRITICAL HIT!!!** '
            amount *= crit_mod
        
        if amount == 0 and is_crit:
            response += f'{interaction.user.display_name} farted so hard, they blew {user.display_name} out of Jail. They are free!\n'
            response += await self.release_user(guild_id, interaction.user.id, user)
            
            if not response:
                response +=  f'Something went wrong, user {user.display_name} could not be released.'
        else:
            if amount >= 0:
                response += f'Their jail sentence was increased by `{amount}` minutes. '
            elif amount < 0: 
                response += f'Their jail sentence was reduced by `{abs(amount)}` minutes. '
            
            time_now = datetime.datetime.now()
            self.event_manager.dispatch_jail_event(time_now, guild_id, command.name, interaction.user.id, amount, affected_jail.get_id())
            
            remaining = self.event_manager.get_jail_remaining(affected_jail)
            response += f'`{BotUtil.strfdelta(remaining, inputtype='minutes')}` still remain.'

        return response
        
    async def jail_user(self, guild_id: int, jailed_by_id: int, user: discord.Member, duration: int) -> bool:
        active_jails = self.database.get_active_jails_by_guild(guild_id)
        jailed_members = [jail.get_member_id() for jail in active_jails]
        
        jail_role = self.settings.get_jail_role(guild_id)
        
        if user.id in jailed_members or user.get_role(jail_role) is not None:
            return False
        
        await user.add_roles(self.bot.get_guild(guild_id).get_role(jail_role))
        
        time_now = datetime.datetime.now()
        jail = UserJail(guild_id, user.id, time_now)
        
        jail = self.database.log_jail_sentence(jail)
        self.event_manager.dispatch_jail_event(time_now, guild_id, JailEventType.JAIL, jailed_by_id, duration, jail.get_id())
        
        return True
    
    async def release_user(self, guild_id: int, released_by_id: int, user: discord.Member) -> str:
        active_jails = self.database.get_active_jails_by_guild(guild_id)
        jailed_members = [jail.get_member_id() for jail in active_jails]
        
        jail_role = self.settings.get_jail_role(guild_id)
        
        if user.id not in jailed_members or user.get_role(jail_role) is None:
            return False
        
        
        await user.remove_roles(user.get_role(jail_role))
        
        affected_jails = self.database.get_active_jails_by_member(guild_id, user.id)
                
        if len(affected_jails) > 0:
            jail = affected_jails[0]
            remaining = self.event_manager.get_jail_remaining(jail)
            response = f'Their remaining sentence of `{BotUtil.strfdelta(remaining, inputtype='minutes')}` will be forgiven.'
            self.event_manager.dispatch_jail_event(datetime.datetime.now(), guild_id, JailEventType.RELEASE, released_by_id, 0, jail.get_id())
        
        return response
    
    @tasks.loop(seconds=20)
    async def jail_check(self):
        self.logger.debug("sys", f'Jail Check task started', cog=self.__cog_name__)
        
        for guild in self.bot.guilds:
            guild_id = guild.id
            self.logger.debug(guild_id, f'Jail Check for guild {guild.name}.', cog=self.__cog_name__)
            active_jails = self.database.get_active_jails_by_guild(guild_id)
            
            for jail in active_jails:
                member = guild.get_member(jail.get_member_id())
                duration = self.event_manager.get_jail_duration(jail)
                remaining = self.event_manager.get_jail_remaining(jail)
                
                self.logger.debug(guild_id, f'Jail Check for {member.name}. Duration: {duration}, Remaining: {remaining}', cog=self.__cog_name__)
                
                if remaining > 0:
                    continue
                    
                jail_role = self.settings.get_jail_role(guild_id)
                jail_channels = self.settings.get_jail_channels(guild_id)
                
                await member.remove_roles(member.get_role(jail_role))
                
                self.logger.log(guild_id, f'User {member.name} was released from jail after {BotUtil.strfdelta(duration, inputtype='minutes')}.', cog=self.__cog_name__)
                
                self.event_manager.dispatch_jail_event(datetime.datetime.now(), guild_id, JailEventType.RELEASE, self.bot.user.id, 0, jail.get_id())
                
                for channel_id in jail_channels:
                    channel = guild.get_channel(channel_id)
                    await channel.send(f'<@{member.id}> was released from jail after {BotUtil.strfdelta(duration, inputtype='minutes')}.')
    
    @jail_check.before_loop
    async def before_jail_check(self):
        await self.bot.wait_until_ready()
    
    @jail_check.after_loop
    async def on_jail_check_cancel(self):
        if self.jail_check.is_being_cancelled():
            self.logger.log(self.__cog_name__, f'Jail check task was cancelled.')
    
    @commands.Cog.listener()
    async def on_ready(self):
        jails = self.database.get_active_jails()
        
        if len(jails) > 0:
            self.logger.log("init",f'Found {len(jails)} ongoing jail sentences.', cog=self.__cog_name__)
        
        for jail in jails:
            guild_id = jail.get_guild_id()
            member_id = jail.get_member_id()
            jail_id = jail.get_id()
            member = None
            guild = self.bot.get_guild(guild_id)
            member = guild.get_member(member_id) if guild is not None else None
                
            if member is None :
                self.logger.log("init",f'Member or guild not found, user {member_id} was marked as released.', cog=self.__cog_name__)
                self.event_manager.dispatch_jail_event(datetime.datetime.now(), guild_id, JailEventType.RELEASE, self.bot.user.id, 0, jail_id)
                continue
            
            jail_role = self.settings.get_jail_role(guild_id)
        
            if member.get_role(jail_role) is None:
                self.logger.log("init",f'Member {member.name} did not have the jail role, applying jail role now.', cog=self.__cog_name__)
                await member.add_roles(self.bot.get_guild(guild_id).get_role(jail_role))
                
            remaining = self.event_manager.get_jail_remaining(jail)
            
            self.logger.log("init",f'Continuing jail sentence of {member.name} in {guild.name}. Remaining duration: {BotUtil.strfdelta(remaining, inputtype='minutes')}', cog=self.__cog_name__)
        
        
        self.jail_check.start()
        
        self.logger.log("init",str(self.__cog_name__) + " loaded.", cog=self.__cog_name__)
    
    @app_commands.command(name="jail", description='Jail a user.')
    @app_commands.describe(
        user='User who will be jailed.',
        duration='Length of the jail sentence. (in minutes)'
        )
    @app_commands.guild_only()
    async def jail(self, interaction: discord.Interaction, user: discord.Member, duration: app_commands.Range[int, 1]):
        if not self.__has_mod_permission(interaction):
            raise app_commands.MissingPermissions([])
        
        if not await self.__check_enabled(interaction):
            return
        
        guild_id = interaction.guild_id
        
        success = await self.jail_user(guild_id, interaction.user.id, user, duration)
        
        if not success:
            await self.bot.command_response(self.__cog_name__, interaction, f'User {user.name} is already in jail.', user.name, args=[duration])
            return
        
        timestamp_now = int(datetime.datetime.now().timestamp())
        release = timestamp_now + (duration*60)
        
        await interaction.channel.send(f'<@{user.id}> was sentenced to Jail by <@{interaction.user.id}> . They will be released <t:{release}:R>.', delete_after=(duration*60))
        
        await self.bot.command_response(self.__cog_name__, interaction, f'User {user.name} jailed successfully.', user.name, args=[duration])

    @app_commands.command(name="release", description='Resease a user from jail.')
    @app_commands.describe(
        user='Resease this user from jail.'
        )
    @app_commands.guild_only()
    async def release(self, interaction: discord.Interaction, user: discord.Member):
        if not self.__has_mod_permission(interaction):
            raise app_commands.MissingPermissions([])
        
        if not await self.__check_enabled(interaction):
            return
        
        guild_id = interaction.guild_id
        jail_role = self.settings.get_jail_role(guild_id)
        
        if user.get_role(jail_role) is None:
            await self.bot.command_response(self.__cog_name__, interaction, f'User {user.display_name} is currently not in jail.', args=[user])
            return
            
        response = await self.release_user(guild_id, interaction.user.id, user)
        
        if not response:
            await self.bot.command_response(self.__cog_name__, interaction, f'Something went wrong, user {user.display_name} could not be released.', args=[user])
            return
        
        response = f'<@{user.id}> was released from Jail by <@{interaction.user.id}>. ' + response

        await interaction.channel.send(response)
        
        await self.bot.command_response(self.__cog_name__, interaction, f'User {user.display_name} released successfully.', args=[user])

    group = app_commands.Group(name="degenjail", description="Subcommands for the Jail module.")

    @group.command(name="settings", description="Overview of all jail related settings and their current value.")
    @app_commands.check(__has_permission)
    async def get_settings(self, interaction: discord.Interaction):
        output = self.settings.get_settings_string(interaction.guild_id, BotSettings.JAIL_SUBSETTINGS_KEY)
        await self.bot.command_response(self.__cog_name__, interaction, output)
    
    @group.command(name="toggle", description="Enable or disable the entire jail module.")
    @app_commands.describe(enabled='Turns the jail module on or off.')
    @app_commands.check(__has_permission)
    async def set_toggle(self, interaction: discord.Interaction, enabled: Literal['on', 'off']): 
        self.settings.set_jail_enabled(interaction.guild_id, enabled == "on")
        await self.bot.command_response(self.__cog_name__, interaction, f'Jail module was turned {enabled}.', args=[enabled])
    
    @group.command(name="add_channel", description='Enable jail interactions for a channel.')
    @app_commands.describe(channel='The jail channel.')
    @app_commands.check(__has_permission)
    async def add_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        self.settings.add_jail_channel(interaction.guild_id, channel.id)
        await self.bot.command_response(self.__cog_name__, interaction, f'Added {channel.name} to jail channels.', args=[channel.name])
        
    @group.command(name="remove_channel", description='Disable jail interactions for a channel.')
    @app_commands.describe(channel='Removes this channel from the jail channels.')
    @app_commands.check(__has_permission)
    async def remove_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        self.settings.remove_jail_channel(interaction.guild_id, channel.id)
        await self.bot.command_response(self.__cog_name__, interaction, f'Removed {channel.name} from jail channels.', args=[channel.name])
    
    @group.command(name="add_mod_role", description='Add jail privileges to a role.')
    @app_commands.describe(role='This role will be allowed to jail users.')
    @app_commands.check(__has_permission)
    async def add_mod_role(self, interaction: discord.Interaction, role: discord.Role):
        self.settings.add_jail_mod_role(interaction.guild_id, role.id)
        await self.bot.command_response(self.__cog_name__, interaction, f'Added {role.name} to jail moderators.', args=[role.name])
        
    @group.command(name="remove_mod_role", description='Remove jail privileges from a role.')
    @app_commands.describe(role='Removes role from jail mods.')
    @app_commands.check(__has_permission)
    async def remove_mod_role(self, interaction: discord.Interaction, role: discord.Role):
        self.settings.remove_jail_mod_role(interaction.guild_id, role.id)
        await self.bot.command_response(self.__cog_name__, interaction, f'Removed {role.name} from jail moderators.', args=[role.name])
    
    @group.command(name="set_jailed_role", description="Sets the role for jailed people.")
    @app_commands.describe(role='The role for jailed users.')
    @app_commands.check(__has_permission)
    async def set_jailed_role(self, interaction: discord.Interaction, role: discord.Role):
        self.settings.set_jail_role(interaction.guild_id, role.id)
        await self.bot.command_response(self.__cog_name__, interaction, f'Jail role was set to `{role.name}` .', args=[role.name])

    
    @group.command(name="setup", description="Opens a dialog to edit various jail settings.")
    @app_commands.check(__has_permission)
    async def setup(self, interaction: discord.Interaction):
        current_slap_time = self.settings.get_jail_slap_time(interaction.guild_id)
        current_pet_time = self.settings.get_jail_pet_time(interaction.guild_id)
        current_fart_min = self.settings.get_jail_fart_min(interaction.guild_id)
        current_fart_max = self.settings.get_jail_fart_max(interaction.guild_id)
        current_base_crit = self.settings.get_jail_base_crit_rate(interaction.guild_id)

        modal = JailSettingsModal(self.bot, self.settings)
        modal.slap_time.default = current_slap_time
        modal.pet_time.default = current_pet_time
        modal.fart_min_time.default = current_fart_min
        modal.fart_max_time.default = current_fart_max
        modal.base_crit_rate.default = str(current_base_crit)
        
        await interaction.response.send_modal(modal)
                
async def setup(bot):
    await bot.add_cog(Jail(bot))
