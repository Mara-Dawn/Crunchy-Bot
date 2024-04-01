import datetime
import random
import typing
import discord

from discord.ext import commands
from discord import app_commands
from typing import *
from BotSettings import BotSettings
from CrunchyBot import CrunchyBot
from cogs.beans.BeansGroup import BeansGroup
from events.BeansEventType import BeansEventType
from view.SettingsModal import SettingsModal

class BeansBasics(BeansGroup):
    
    def __init__(self, bot: CrunchyBot):
        super().__init__(bot)

    async def __has_permission(interaction: discord.Interaction) -> bool:
        author_id = 90043934247501824
        return interaction.user.id == author_id or interaction.user.guild_permissions.administrator
    
    async def __check_enabled(self, interaction: discord.Interaction) -> bool:
        guild_id = interaction.guild_id
        
        if not self.settings.get_beans_enabled(guild_id):
            await self.bot.command_response(self.__cog_name__, interaction, f'Beans module is currently disabled.')
            return False
        
        if interaction.channel_id not in self.settings.get_beans_channels(guild_id):
            await self.bot.command_response(self.__cog_name__, interaction, f'Beans commands cannot be used in this channel.')
            return False
        
        return True

    @commands.Cog.listener('on_ready')
    async def on_ready_beansbasics(self):
        self.logger.log("init", "BeansBasics loaded.", cog=self.__cog_name__)
    
    @app_commands.command(name="please", description='Your daily dose of beans.')
    @app_commands.guild_only()
    async def please(self, interaction: discord.Interaction):
        if not await self.__check_enabled(interaction):
            return 
        
        guild_id = interaction.guild_id
        user_id = interaction.user.id
        
        last_daily_beans_event = self.database.get_last_beans_event(guild_id, user_id, BeansEventType.DAILY)
        
        if last_daily_beans_event is not None: 
        
            current_date = datetime.datetime.now().date()
            last_daily_beans_date = last_daily_beans_event.get_datetime().date()
        
            if current_date == last_daily_beans_date:
                await self.bot.command_response(self.__cog_name__, interaction, f'You already got your daily beans, dummy! Try again tomorrow.', ephemeral=False)
                return
        
        beans_daily_min = self.settings.get_beans_daily_min(guild_id)
        beans_daily_max = self.settings.get_beans_daily_max(guild_id)

        amount = random.randint(beans_daily_min, beans_daily_max)
        
        self.event_manager.dispatch_beans_event(
            datetime.datetime.now(), 
            guild_id, 
            BeansEventType.DAILY, 
            user_id, 
            amount
        )
        await self.bot.command_response(self.__cog_name__, interaction, f'<@{user_id}> got their daily dose of `🅱️{amount}` beans.', args=[amount], ephemeral=False)
    
    @app_commands.command(name="balance", description='Your current bean balance.')
    @app_commands.describe(
        user='Optional, check this users bean balance.'
        )
    @app_commands.guild_only()
    async def balance(self, interaction: discord.Interaction, user: typing.Optional[discord.Member] = None):
        if not await self.__check_enabled(interaction):
            return 
        
        user = user if user is not None else interaction.user
        user_id = user.id
        
        guild_id = interaction.guild_id
        
        current_balance = self.database.get_member_beans(guild_id, user_id)
        
        await self.bot.command_response(self.__cog_name__, interaction, f'<@{user_id}> currently has `🅱️{current_balance}` beans.', args=[user.display_name], ephemeral=False)
    
    @app_commands.command(name="grant", description="Give or remove beans from specific users. (Admin only)")
    @app_commands.describe(
        user='User to give beans to.',
        amount='Amount of beans, can be negative.'
        )
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def grant(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        
        guild_id = interaction.guild_id
        
        self.event_manager.dispatch_beans_event(
            datetime.datetime.now(), 
            guild_id,
            BeansEventType.BALANCE_CHANGE, 
            user.id,
            amount
        )
        
        response = f'`🅱️{abs(amount)}` beans were '
        if amount >= 0:
            response += 'added to '
        else:
            response += 'subtracted from '
        
        response += f'<@{user.id}>\'s bean balance by <@{interaction.user.id}>'
            
        await self.bot.command_response(self.__cog_name__, interaction, response, args=[user.display_name, amount], ephemeral=False)
    
    @app_commands.command(name="transfer", description="Transfer your beans to other users.")
    @app_commands.describe(
        user='User to transfer beans to.',
        amount='Amount of beans.'
        )
    @app_commands.guild_only()
    async def transfer(self, interaction: discord.Interaction, user: discord.Member, amount: app_commands.Range[int, 1]):
        await interaction.response.defer()
        
        guild_id = interaction.guild_id
        user_id = interaction.user.id
        
        current_balance = self.database.get_member_beans(guild_id, user_id)
        
        if current_balance < amount:
            await self.bot.command_response(self.__cog_name__, interaction, f'You dont have that many beans, idiot.', ephemeral=False)
            return
        now = datetime.datetime.now()
        
        self.event_manager.dispatch_beans_event(
            now, 
            guild_id,
            BeansEventType.USER_TRANSFER, 
            interaction.user.id,
            -amount
        )
        
        self.event_manager.dispatch_beans_event(
            now, 
            guild_id,
            BeansEventType.USER_TRANSFER, 
            user.id,
            amount
        )
        
        response = f'`🅱️{abs(amount)}` beans were transferred from <@{interaction.user.id}> to <@{user.id}>.'
            
        await self.bot.command_response(self.__cog_name__, interaction, response, args=[interaction.user.display_name,user.display_name, amount], ephemeral=False)
    
    @app_commands.command(name="settings", description="Overview of all beans related settings and their current value.")
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def get_settings(self, interaction: discord.Interaction):
        output = self.settings.get_settings_string(interaction.guild_id, BotSettings.BEANS_SUBSETTINGS_KEY)
        await self.bot.command_response(self.__cog_name__, interaction, output)
    
    @app_commands.command(name="toggle", description="Enable or disable the entire beans module.")
    @app_commands.describe(enabled='Turns the beans module on or off.')
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def set_toggle(self, interaction: discord.Interaction, enabled: Literal['on', 'off']):
        self.settings.set_beans_enabled(interaction.guild_id, enabled == "on")
        await self.bot.command_response(self.__cog_name__, interaction, f'Beans module was turned {enabled}.', args=[enabled])
       
    @app_commands.command(name="daily_setup", description="Opens a dialog to edit various daily and bonus beans settings.")
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def daily_setup(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        modal = SettingsModal(self.bot, self.settings, self.__cog_name__, interaction.command.name, "Settings for Daily Beans related Features")
        
        modal.add_field(guild_id, BotSettings.BEANS_SUBSETTINGS_KEY, BotSettings.BEANS_DAILY_MIN_KEY, int)
        modal.add_field(guild_id, BotSettings.BEANS_SUBSETTINGS_KEY, BotSettings.BEANS_DAILY_MAX_KEY, int)
        modal.add_field(guild_id, BotSettings.BEANS_SUBSETTINGS_KEY, BotSettings.BEANS_BONUS_CARD_AMOUNT_10_KEY, int)
        modal.add_field(guild_id, BotSettings.BEANS_SUBSETTINGS_KEY, BotSettings.BEANS_BONUS_CARD_AMOUNT_25_KEY, int)
        
        modal.add_constraint([BotSettings.BEANS_DAILY_MIN_KEY, BotSettings.BEANS_DAILY_MAX_KEY], lambda a,b: a <= b , 'Beans minimum must be smaller than Beans maximum.')
        
        await interaction.response.send_modal(modal)
        
    @app_commands.command(name="add_channel", description='Enable beans commands for a channel.')
    @app_commands.describe(channel='The beans channel.')
    @app_commands.check(__has_permission)
    async def add_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        self.settings.add_beans_channel(interaction.guild_id, channel.id)
        await self.bot.command_response(self.__cog_name__, interaction, f'Added {channel.name} to beans channels.', args=[channel.name])
        
    @app_commands.command(name="remove_channel", description='Disable beans commands for a channel.')
    @app_commands.describe(channel='Removes this channel from the beans channels.')
    @app_commands.check(__has_permission)
    async def remove_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        self.settings.remove_beans_channel(interaction.guild_id, channel.id)
        await self.bot.command_response(self.__cog_name__, interaction, f'Removed {channel.name} from beans channels.', args=[channel.name])
    
async def setup(bot):
    await bot.add_cog(BeansBasics(bot))
