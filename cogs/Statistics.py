import datetime
import discord

from discord.ext import tasks, commands
from discord import app_commands
from typing import Dict, Literal
from BotLogger import BotLogger
from BotSettings import BotSettings
from MaraBot import MaraBot
from datalayer.JailList import JailList
from datalayer.UserInteraction import UserInteraction

class Statistics(commands.Cog):
    
    def __init__(self, bot: MaraBot):
        self.bot = bot
        
        self.logger: BotLogger = bot.logger
        self.settings: BotSettings = bot.settings
        
    
    async def __has_permission(interaction: discord.Interaction) -> bool:
        
        author_id = 90043934247501824
        return interaction.user.id == author_id or interaction.user.guild_permissions.administrator
    
    async def __has_mod_permission(self, interaction: discord.Interaction) -> bool:
        
        author_id = 90043934247501824
        roles = self.settings.get_jail_mod_roles(interaction.guild_id)
        is_mod = bool(set([x.id for x in interaction.user.roles]).intersection(roles))
        return interaction.user.id == author_id or interaction.user.guild_permissions.administrator or is_mod
    
    
    async def user_command_interaction(self, interaction: discord.Interaction, user: discord.Member):
        
        command = interaction.command
        
        command_type = None
        
        match command.name:
            case "slap":
                command_type = UserInteraction.SLAP
            case "pet":
                command_type = UserInteraction.PET
            case "fart":
                command_type = UserInteraction.FART
        
        log_message = f'{interaction.user.name} used command `{command.name}` on {user.name}.'
        self.logger.log(interaction.guild_id, log_message, cog=self.__cog_name__)
        
        guild_id = interaction.guild_id
        invoker = interaction.user
        
        list = self.jail_list[guild_id]
        
        jail_role = self.settings.get_jail_role(guild_id)
        jail_channels = self.settings.get_jail_channels(guild_id)
        
        if list.has_user(user.id) and user.get_role(jail_role) is not None and interaction.channel_id in jail_channels:
            
            user_node = list.get_user(user.id)
            self.logger.log(guild_id, f'{command.name}: targeted user {user.name} is in jail.', cog=self.__cog_name__)
            
            if invoker.id in user_node.get_list(command_type):
                self.logger.log(guild_id, self.__get_already_used_log_msg(command_type, interaction, user), cog=self.__cog_name__)
                await interaction.response.send_message(self.__get_already_used_msg(command_type, interaction, user))
                return

            response = self.__get_response(command_type, interaction, user)
            
            response += '\n' + user_node.apply_interaction(command_type, interaction, user, self.settings)

            await interaction.response.send_message(response)
            
            return
        
        await interaction.response.send_message(self.__get_response(command_type, interaction, user))

    @app_commands.command(name="slap")
    @app_commands.describe(
        user='Slap this bitch.',
        )
    @app_commands.guild_only()
    async def slap(self, interaction: discord.Interaction, user: discord.Member):
        
        await self.user_command_interaction(interaction, user)
    
    @app_commands.command(name="pet")
    @app_commands.describe(
        user='Give them a pat.',
        )
    @app_commands.guild_only()
    async def pet(self, interaction: discord.Interaction, user: discord.Member):
        
        await self.user_command_interaction(interaction, user)

    @app_commands.command(name="fart")
    @app_commands.describe(
        user='Fart on this user.',
        )
    @app_commands.guild_only()
    async def fart(self, interaction: discord.Interaction, user: discord.Member):
        
        await self.user_command_interaction(interaction, user)
    
    @app_commands.command(name="jail")
    @app_commands.describe(
        user='User who will be jailed.',
        duration='Length of the jail sentence.  (in minutes)'
        )
    @app_commands.guild_only()
    async def jail(self, interaction: discord.Interaction, user: discord.Member, duration: app_commands.Range[int, 1]):
        
        if not self.__has_mod_permission:
            raise app_commands.MissingPermissions([])
        
        guild_id = interaction.guild_id
        
        list = self.jail_list[guild_id]
        
        jail_role = self.settings.get_jail_role(guild_id)
        
        if list.has_user(user.id) or user.get_role(jail_role) is not None:
            await self.bot.command_response(self.__cog_name__, interaction, f'User {user.name} is already in jail.')
            return
            
        list.add_user(user.id, datetime.datetime.now(), duration)
        
        await user.add_roles(self.bot.get_guild(guild_id).get_role(jail_role))
        
        timestamp_now = int(datetime.datetime.now().timestamp())
        release = timestamp_now + (duration*60)
        await interaction.channel.send(f'<@{user.id}> was sentenced to Jail by <@{interaction.user.id}> . They will be released <t:{release}:R>.', delete_after=(duration*60))
        
        await self.bot.command_response(self.__cog_name__, interaction, f'User {user.name} jailed successfully.')


    @app_commands.command(name="release")
    @app_commands.describe(
        user='Resease this user from jail.'
        )
    @app_commands.guild_only()
    async def release(self, interaction: discord.Interaction, user: discord.Member):
        
        if not self.__has_mod_permission:
            raise app_commands.MissingPermissions([])
        
        guild_id = interaction.guild_id
        
        list = self.jail_list[guild_id]
        
        jail_role = self.settings.get_jail_role(guild_id)
        
        if user.get_role(jail_role) is not None:
            await user.remove_roles(user.get_role(jail_role))
        
        response = f'<@{user.id}> was released from Jail by <@{interaction.user.id}>.'
        
        if list.has_user(user.id):
            
            user_node = list.get_user(user.id)
            response += f' Their remaining sentence of {user_node.get_remaining_str()} will be forgiven.'
            
            list.remove_user(user.id)
        
        
        await interaction.channel.send(response)
        
        await self.bot.command_response(self.__cog_name__, interaction, f'User {user.name} released successfully.', user)


    group = app_commands.Group(name="degenjail", description="Subcommands for the Jail module.")

    @group.command(name="settings")
    @app_commands.check(__has_permission)
    async def get_settings(self, interaction: discord.Interaction):
        
        output = self.settings.get_settings_string(interaction.guild_id, BotSettings.JAIL_SUBSETTINGS_KEY)
        
        await self.bot.command_response(self.__cog_name__, interaction, output)
    
    @group.command(name="toggle")
    @app_commands.describe(enabled='Turns the police module on or off.')
    @app_commands.check(__has_permission)
    async def set_toggle(self, interaction: discord.Interaction, enabled: Literal['on', 'off']):
        
        self.settings.set_jail_enabled(interaction.guild_id, enabled == "on")
        
        await self.bot.command_response(self.__cog_name__, interaction, f'Police module was turned {enabled}.')
    
    @group.command(name="set_jailed_role")
    @app_commands.describe(role='The role for jailed users.')
    @app_commands.check(__has_permission)
    async def set_jailed_role(self, interaction: discord.Interaction, role: discord.Role):
        
        self.settings.set_jail_role(interaction.guild_id, role.id)
        await self.bot.command_response(self.__cog_name__, interaction, f'Jail role was set to `{role.name}` .')
    
    @group.command(name="add_channel")
    @app_commands.describe(channel='The jail channel.')
    @app_commands.check(__has_permission)
    async def add_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        
        self.settings.add_jail_channel(interaction.guild_id, channel.id)
        await self.bot.command_response(self.__cog_name__, interaction, f'Added {channel.name} to jail channels.')
        
    @group.command(name="remove_channel")
    @app_commands.describe(channel='Removes this channel from the jail channels.')
    @app_commands.check(__has_permission)
    async def remove_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        
        self.settings.remove_jail_channel(interaction.guild_id, channel.id)
        await self.bot.command_response(self.__cog_name__, interaction, f'Removed {channel.name} from jail channels.')
    
    @group.command(name="add_mod_role")
    @app_commands.describe(role='This role will be allowed to jail users.')
    @app_commands.check(__has_permission)
    async def add_mod_role(self, interaction: discord.Interaction, role: discord.Role):
        
        self.settings.add_jail_mod_role(interaction.guild_id, role.id)
        await self.bot.command_response(self.__cog_name__, interaction, f'Added {role.name} to jail moderators.')
        
    @group.command(name="remove_mod_role")
    @app_commands.describe(role='Removes role from jail mods.')
    @app_commands.check(__has_permission)
    async def remove_mod_role(self, interaction: discord.Interaction, role: discord.Role):
        
        self.settings.remove_jail_mod_role(interaction.guild_id, role.id)
        await self.bot.command_response(self.__cog_name__, interaction, f'Removed {role.name} from jail moderators.')
    
    @group.command(name="set_interaction_times")
    @app_commands.describe(
        slap='Amount of time added to jail sentence when user gets slapped.',
        pet='Amount of time subtracted from jail sentence when user gets a pet.',
        fart_min='Minimum amount of time added to jail sentence when user gets farted on.',
        fart_max='Maximum amount of time added to jail sentence when user gets farted on.',
        )
    @app_commands.check(__has_permission)
    async def set_interaction_times(self, interaction: discord.Interaction, slap: app_commands.Range[int, 0] ,pet: app_commands.Range[int, 0], fart_min: int, fart_max: int):
        
        if fart_min > fart_max:
            await self.bot.command_response(self.__cog_name__, interaction, f'fart_min must be smaller than fart_max.')
            return
            
        self.settings.set_jail_slap_time(interaction.guild_id, slap)
        self.settings.set_jail_pet_time(interaction.guild_id, pet)
        self.settings.set_jail_fart_min(interaction.guild_id, fart_min)
        self.settings.set_jail_fart_max(interaction.guild_id, fart_max)
        
        await self.bot.command_response(self.__cog_name__, interaction, f'Interactions updated: Slaps: +{slap} minutes. Pets: -{pet} minutes. Farts: {fart_min} to {fart_max} minutes.')
                
async def setup(bot):
    await bot.add_cog(Statistics(bot))
