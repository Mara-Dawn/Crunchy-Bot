
import datetime
from typing import Literal

import discord
from bot import CrunchyBot
from bot_util import BotUtil
from control.controller import Controller
from control.event_manager import EventManager
from control.item_manager import ItemManager
from control.jail_manager import JailManager
from control.logger import BotLogger
from control.role_manager import RoleManager
from control.settings_manager import SettingsManager
from datalayer.database import Database
from discord import app_commands
from discord.ext import commands, tasks
from events.jail_event import JailEvent
from events.types import JailEventType
from view.settings_modal import SettingsModal


class Jail(commands.Cog):
    
    def __init__(self, bot: CrunchyBot):
        self.bot = bot
        self.controller: Controller = bot.controller
        self.logger: BotLogger = bot.logger
        self.database: Database = bot.database
        self.item_manager: ItemManager = self.controller.get_service(ItemManager)
        self.event_manager: EventManager = self.controller.get_service(EventManager)
        self.role_manager: RoleManager = self.controller.get_service(RoleManager)
        self.jail_manager: JailManager = self.controller.get_service(JailManager)
        self.settings_manager: SettingsManager = self.controller.get_service(
            SettingsManager
        )

    @staticmethod
    async def __has_permission(interaction: discord.Interaction) -> bool:
        author_id = 90043934247501824
        return interaction.user.id == author_id or interaction.user.guild_permissions.administrator
    
    async def __has_mod_permission(self, interaction: discord.Interaction) -> bool:
        author_id = 90043934247501824
        roles = await self.settings_manager.get_jail_mod_roles(interaction.guild_id)
        is_mod = len(set([x.id for x in interaction.user.roles]).intersection(roles)) > 0
        return interaction.user.id == author_id or interaction.user.guild_permissions.administrator or is_mod
    
    async def __check_enabled(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        if not await self.settings_manager.get_jail_enabled(guild_id):
            await self.bot.command_response(self.__cog_name__, interaction, 'Jail module is currently disabled.')
            return False
        return True
    
    @tasks.loop(seconds=20)
    async def jail_check(self):
        self.logger.debug("sys", 'Jail Check task started', cog=self.__cog_name__)
        
        for guild in self.bot.guilds:
            guild_id = guild.id
            self.logger.debug(guild_id, f'Jail Check for guild {guild.name}.', cog=self.__cog_name__)
            active_jails = await self.database.get_active_jails_by_guild(guild_id)
            
            for jail in active_jails:
                member = guild.get_member(jail.member_id)
                duration = await self.jail_manager.get_jail_duration(jail)
                remaining = await self.jail_manager.get_jail_remaining(jail)
                
                self.logger.debug(guild_id, f'Jail Check for {member.name}. Duration: {duration}, Remaining: {remaining}', cog=self.__cog_name__)
                
                if remaining > 0:
                    continue
                    
                jail_role = await self.settings_manager.get_jail_role(guild_id)
                jail_channels = await self.settings_manager.get_jail_channels(guild_id)
                
                await member.remove_roles(member.get_role(jail_role))
                
                self.logger.log(guild_id, f'User {member.name} was released from jail after {BotUtil.strfdelta(duration, inputtype='minutes')}.', cog=self.__cog_name__)
                
                time_now = datetime.datetime.now()
                event = JailEvent(time_now, guild_id, JailEventType.RELEASE, self.bot.user.id, 0, jail.id)
                await self.controller.dispatch_event(event)
                
                for channel_id in jail_channels:
                    channel = guild.get_channel(channel_id)
                    await channel.send(f'<@{member.id}> was released from jail after {BotUtil.strfdelta(duration, inputtype='minutes')}.')
    
    @jail_check.before_loop
    async def before_jail_check(self):
        await self.bot.wait_until_ready()
    
    @jail_check.after_loop
    async def on_jail_check_cancel(self):
        # pylint: disable-next=no-member
        if self.jail_check.is_being_cancelled():
            self.logger.log(self.__cog_name__, 'Jail check task was cancelled.')
    
    @commands.Cog.listener()
    async def on_ready(self):
        jails = await self.database.get_active_jails()
        
        if len(jails) > 0:
            self.logger.log("init",f'Found {len(jails)} ongoing jail sentences.', cog=self.__cog_name__)
        
        for jail in jails:
            guild_id = jail.guild_id
            member_id = jail.member_id
            member = None
            guild = self.bot.get_guild(guild_id)
            member = guild.get_member(member_id) if guild is not None else None
                
            if member is None :
                self.logger.log("init",f'Member or guild not found, user {member_id} was marked as released.', cog=self.__cog_name__)
                
                time_now = datetime.datetime.now()
                event = JailEvent(time_now, guild_id, JailEventType.RELEASE, self.bot.user.id, 0, jail.id)
                await self.controller.dispatch_event(event)
                
                continue
            
            jail_role = await self.settings_manager.get_jail_role(guild_id)
        
            if member.get_role(jail_role) is None:
                self.logger.log("init",f'Member {member.name} did not have the jail role, applying jail role now.', cog=self.__cog_name__)
                await member.add_roles(self.bot.get_guild(guild_id).get_role(jail_role))
                
            remaining = await self.jail_manager.get_jail_remaining(jail)
            
            self.logger.log("init",f'Continuing jail sentence of {member.name} in {guild.name}. Remaining duration: {BotUtil.strfdelta(remaining, inputtype='minutes')}', cog=self.__cog_name__)
        
        # pylint: disable-next=no-member
        self.jail_check.start()
        
        self.logger.log("init",str(self.__cog_name__) + " loaded.", cog=self.__cog_name__)
    
    @app_commands.command(name="jail", description='Jail a user.')
    @app_commands.describe(
        user='User who will be jailed.',
        duration='Length of the jail sentence. (in minutes)'
        )
    @app_commands.guild_only()
    async def jail(self, interaction: discord.Interaction, user: discord.Member, duration: app_commands.Range[int, 1]):
        if not await self.__has_mod_permission(interaction):
            raise app_commands.MissingPermissions([])
        
        if not await self.__check_enabled(interaction):
            return
        
        guild_id = interaction.guild_id
        
        success = await self.jail_manager.jail_user(guild_id, interaction.user.id, user, duration)
        
        if not success:
            await self.bot.command_response(self.__cog_name__, interaction, f'User {user.name} is already in jail.', args=[user.name, duration])
            return
        
        timestamp_now = int(datetime.datetime.now().timestamp())
        release = timestamp_now + (duration*60)
        
        await self.jail_manager.announce(interaction.guild, f'<@{user.id}> was sentenced to Jail by <@{interaction.user.id}> . They will be released <t:{release}:R>.', delete_after=(duration*60))
        
        await self.bot.command_response(self.__cog_name__, interaction, f'User {user.name} jailed successfully.', args=[user.name, duration])

    @app_commands.command(name="release", description='Resease a user from jail.')
    @app_commands.describe(
        user='Resease this user from jail.'
        )
    @app_commands.guild_only()
    async def release(self, interaction: discord.Interaction, user: discord.Member):
        if not await self.__has_mod_permission(interaction):
            raise app_commands.MissingPermissions([])
        
        if not await self.__check_enabled(interaction):
            return
        
        guild_id = interaction.guild_id
        jail_role = await self.settings_manager.get_jail_role(guild_id)
        
        if user.get_role(jail_role) is None:
            await self.bot.command_response(self.__cog_name__, interaction, f'User {user.display_name} is currently not in jail.', args=[user])
            return

        if interaction.user.guild_permissions.administrator and interaction.user.id == user.id:
            response = f'<@{interaction.user.id}> tried to abuse their mod privileges by freeing themselves with admin powers. BUT NOT THIS TIME!'
            await self.jail_manager.announce(interaction.guild, response)
            await self.bot.command_response(self.__cog_name__, interaction, 'lmao', args=[user])
            return
        
        response = await self.jail_manager.release_user(guild_id, interaction.user.id, user)
        
        if not response:
            await self.bot.command_response(self.__cog_name__, interaction, f'Something went wrong, user {user.display_name} could not be released.', args=[user])
            return
        
        response = f'<@{user.id}> was released from Jail by <@{interaction.user.id}>. ' + response

        await self.jail_manager.announce(interaction.guild, response)
        
        await self.bot.command_response(self.__cog_name__, interaction, f'User {user.display_name} released successfully.', args=[user])

    group = app_commands.Group(name="degenjail", description="Subcommands for the Jail module.")

    @group.command(name="settings", description="Overview of all jail related settings and their current value.")
    @app_commands.check(__has_permission)
    async def get_settings(self, interaction: discord.Interaction):
        output = await self.settings_manager.get_settings_string(interaction.guild_id, SettingsManager.JAIL_SUBSETTINGS_KEY)
        await self.bot.command_response(self.__cog_name__, interaction, output)
    
    @group.command(name="toggle", description="Enable or disable the entire jail module.")
    @app_commands.describe(enabled='Turns the jail module on or off.')
    @app_commands.check(__has_permission)
    async def set_toggle(self, interaction: discord.Interaction, enabled: Literal['on', 'off']): 
        await self.settings_manager.set_jail_enabled(interaction.guild_id, enabled == "on")
        await self.bot.command_response(self.__cog_name__, interaction, f'Jail module was turned {enabled}.', args=[enabled])
    
    @group.command(name="add_channel", description='Enable jail interactions for a channel.')
    @app_commands.describe(channel='The jail channel.')
    @app_commands.check(__has_permission)
    async def add_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await self.settings_manager.add_jail_channel(interaction.guild_id, channel.id)
        await self.bot.command_response(self.__cog_name__, interaction, f'Added {channel.name} to jail channels.', args=[channel.name])
        
    @group.command(name="remove_channel", description='Disable jail interactions for a channel.')
    @app_commands.describe(channel='Removes this channel from the jail channels.')
    @app_commands.check(__has_permission)
    async def remove_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await self.settings_manager.remove_jail_channel(interaction.guild_id, channel.id)
        await self.bot.command_response(self.__cog_name__, interaction, f'Removed {channel.name} from jail channels.', args=[channel.name])
    
    @group.command(name="add_mod_role", description='Add jail privileges to a role.')
    @app_commands.describe(role='This role will be allowed to jail users.')
    @app_commands.check(__has_permission)
    async def add_mod_role(self, interaction: discord.Interaction, role: discord.Role):
        await self.settings_manager.add_jail_mod_role(interaction.guild_id, role.id)
        await self.bot.command_response(self.__cog_name__, interaction, f'Added {role.name} to jail moderators.', args=[role.name])
        
    @group.command(name="remove_mod_role", description='Remove jail privileges from a role.')
    @app_commands.describe(role='Removes role from jail mods.')
    @app_commands.check(__has_permission)
    async def remove_mod_role(self, interaction: discord.Interaction, role: discord.Role):
        await self.settings_manager.remove_predictions_mod_role(interaction.guild_id, role.id)
        await self.bot.command_response(self.__cog_name__, interaction, f'Removed {role.name} from jail moderators.', args=[role.name])
    
    @group.command(name="set_jailed_role", description="Sets the role for jailed people.")
    @app_commands.describe(role='The role for jailed users.')
    @app_commands.check(__has_permission)
    async def set_jailed_role(self, interaction: discord.Interaction, role: discord.Role):
        await self.settings_manager.set_jail_role(interaction.guild_id, role.id)
        await self.bot.command_response(self.__cog_name__, interaction, f'Jail role was set to `{role.name}` .', args=[role.name])

    
    @group.command(name="setup", description="Opens a dialog to edit various jail settings.")
    @app_commands.check(__has_permission)
    async def setup(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        modal = SettingsModal(self.bot, self.settings_manager, self.__cog_name__, interaction.command.name, "Settings for Jail Features")
        
        await modal.add_field(guild_id, SettingsManager.JAIL_SUBSETTINGS_KEY, SettingsManager.JAIL_SLAP_TIME_KEY, int)
        await modal.add_field(guild_id, SettingsManager.JAIL_SUBSETTINGS_KEY, SettingsManager.JAIL_PET_TIME_KEY, int)
        await modal.add_field(guild_id, SettingsManager.JAIL_SUBSETTINGS_KEY, SettingsManager.JAIL_FART_TIME_MIN_KEY, int, allow_negative=True)
        await modal.add_field(guild_id, SettingsManager.JAIL_SUBSETTINGS_KEY, SettingsManager.JAIL_FART_TIME_MAX_KEY, int)
        await modal.add_field(guild_id, SettingsManager.JAIL_SUBSETTINGS_KEY, SettingsManager.JAIL_BASE_CRIT_RATE_KEY, float)
        
        modal.add_constraint([SettingsManager.JAIL_FART_TIME_MIN_KEY, SettingsManager.JAIL_FART_TIME_MAX_KEY], lambda a,b: a <= b , 'fart minimum must be smaller than fart maximum.')
        modal.add_constraint([SettingsManager.JAIL_BASE_CRIT_RATE_KEY], lambda a: a >= 0 and a <= 1 , 'crit rate must be between 0 and 1.')
        
        await interaction.response.send_modal(modal) 
                
async def setup(bot):
    await bot.add_cog(Jail(bot))
