import asyncio
import datetime
import random
import typing
import discord

from discord.ext import commands
from discord import app_commands
from typing import Literal
from BotLogger import BotLogger
from BotSettings import BotSettings
from BotUtil import BotUtil
from MaraBot import MaraBot
from datalayer.Database import Database
from events.BeansEventType import BeansEventType
from events.EventManager import EventManager
from view.BeansDailySettingsModal import BeansDailySettingsModal
from view.BeansGambaSettingsModal import BeansGambaSettingsModal

class Beans(commands.Cog):
    
    def __init__(self, bot: MaraBot):
        self.bot = bot
        self.logger: BotLogger = bot.logger
        self.settings: BotSettings = bot.settings
        self.database: Database = bot.database
        self.event_manager: EventManager = bot.event_manager

    async def __has_permission(interaction: discord.Interaction) -> bool:
        author_id = 90043934247501824
        return interaction.user.id == author_id or interaction.user.guild_permissions.administrator

    async def __check_enabled(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        
        if not self.settings.get_beans_enabled(guild_id):
            await self.bot.command_response(self.__cog_name__, interaction, f'Beans module is currently disabled.')
            return False
        
        if interaction.channel_id not in self.settings.get_beans_channels(guild_id):
            await self.bot.command_response(self.__cog_name__, interaction, f'Beans commands cannot be used in this channel.')
            return False
        
        return True

    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.log("init",str(self.__cog_name__) + " loaded.", cog=self.__cog_name__)
        
    @app_commands.command(name="gamba", description='Gamba away your beans.')
    @app_commands.guild_only()
    async def gamba(self, interaction: discord.Interaction):
        if not await self.__check_enabled(interaction):
            return 
        
        guild_id = interaction.guild_id
        user_id = interaction.user.id
        
        current_balance = self.database.get_member_beans(guild_id, user_id)
        cost = self.settings.get_beans_gamba_cost(guild_id)
        
        if current_balance < cost:
            await self.bot.command_response(self.__cog_name__, interaction, f'You\'re out of beans, idiot.', ephemeral=False)
            return
        
        last_gamba_beans_date = self.database.get_last_beans_event_date(guild_id, user_id, BeansEventType.GAMBA_COST)
        
        if last_gamba_beans_date is not None: 
        
            current_date = datetime.datetime.now()
            last_gamba_beans_date = datetime.datetime.fromtimestamp(last_gamba_beans_date)
            
            delta = current_date - last_gamba_beans_date
            delta_seconds = delta.total_seconds()
            cooldown = self.settings.get_beans_gamba_cooldown(guild_id)*60

            if delta_seconds <= cooldown:
                remaining = cooldown - delta_seconds
                
                await self.bot.command_response(self.__cog_name__, interaction, f'Gamba is on cooldown. Try again in {BotUtil.strfdelta(remaining, inputtype='seconds')}', ephemeral=False)
                return
        
        self.event_manager.dispatch_beans_event(
            datetime.datetime.now(), 
            guild_id, 
            BeansEventType.GAMBA_COST, 
            user_id,
            -cost
        )
        
        response = f'You paid {cost} beans to gamba.'
        
        display_values = [
            '\n**0x**',
            '\n**2x**🎲',
            '\n**3x**🎲🎲',
            '\n**10x**🎲🎲🎲'
        ]
        
        payout = 0
        
        loss = 0.65
        doubling = 0.24
        tripling = 0.1
        jackpot = 0.01 #x10
        
        result = random.random()
        
        if result <= loss:
            final_display = 0
            final = f'\nYou lost. It is what it is.'
        elif result > loss and result <= (loss+doubling):
            final_display = 1
            payout = cost * 2
            final = f'\nYou won! Your payout is `{payout}` beans.'
        elif result > (loss+doubling) and result <= (1-jackpot):
            final_display = 2
            payout = cost * 3
            final = f'\nWow you got lucky! Your payout is `{payout}` beans.'
        elif result > (1-jackpot) and result <= 1:
            final_display = 3
            payout = cost * 10
            final = f'\nJACKPOT!!! Your payout is `{payout}` beans.'
        
        display = display_values[0]
        await self.bot.command_response(self.__cog_name__, interaction, response, ephemeral=False)
        
        message = await interaction.original_response()
        i = 0
        current = i
        while i < 10 or current != final_display:
            current = i % len(display_values)
            display = display_values[current]
            await asyncio.sleep((1/20)*i)
            await message.edit(content=response+display)
            i += 1
        
        self.event_manager.dispatch_beans_event(
            datetime.datetime.now(), 
            guild_id, 
            BeansEventType.GAMBA_PAYOUT, 
            user_id,
            payout
        )
        await message.edit(content=response+display+final)
        
    group = app_commands.Group(name="beans", description="Subcommands for the Beans module.")
    
    @group.command(name="please", description='Your daily dose of beans.')
    @app_commands.guild_only()
    async def please(self, interaction: discord.Interaction):
        if not await self.__check_enabled(interaction):
            return 
        
        guild_id = interaction.guild_id
        user_id = interaction.user.id
        
        last_daily_beans_date = self.database.get_last_beans_event_date(guild_id, user_id, BeansEventType.DAILY)
        
        if last_daily_beans_date is not None: 
        
            current_date = datetime.datetime.now().date()
            last_daily_beans_date = datetime.datetime.fromtimestamp(last_daily_beans_date).date()
        
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
        await self.bot.command_response(self.__cog_name__, interaction, f'<@{user_id}> got their daily dose of `{amount}` beans.', args=[amount], ephemeral=False)
    
    @group.command(name="balance", description='Your current bean balance.')
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
        
        await self.bot.command_response(self.__cog_name__, interaction, f'<@{user_id}> currently has `{current_balance}` beans.', args=[user.display_name], ephemeral=False)
    
    @group.command(name="grant", description="Give or remove beans from specific users. (Admin only)")
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
        
        response = f'`{abs(amount)}` beans were '
        if amount >= 0:
            response += 'added to '
        else:
            response += 'subtracted from '
        
        response += f'<@{user.id}>\'s bean balance by <@{interaction.user.id}>'
            
        await self.bot.command_response(self.__cog_name__, interaction, response, args=[user.display_name, amount], ephemeral=False)
    
    @group.command(name="settings", description="Overview of all beans related settings and their current value.")
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def get_settings(self, interaction: discord.Interaction):
        output = self.settings.get_settings_string(interaction.guild_id, BotSettings.BEANS_SUBSETTINGS_KEY)
        await self.bot.command_response(self.__cog_name__, interaction, output)
    
    @group.command(name="toggle", description="Enable or disable the entire beans module.")
    @app_commands.describe(enabled='Turns the beans module on or off.')
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def set_toggle(self, interaction: discord.Interaction, enabled: Literal['on', 'off']):
        self.settings.set_beans_enabled(interaction.guild_id, enabled == "on")
        await self.bot.command_response(self.__cog_name__, interaction, f'Beans module was turned {enabled}.', args=[enabled])
       
    @group.command(name="daily_setup", description="Opens a dialog to edit various daily beans settings.")
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def daily_setup(self, interaction: discord.Interaction):
        beans_daily_min = self.settings.get_beans_daily_min(interaction.guild_id)
        beans_daily_max = self.settings.get_beans_daily_max(interaction.guild_id)

        modal = BeansDailySettingsModal(self.bot, self.settings)
        modal.beans_daily_min.default = beans_daily_min
        modal.beans_daily_max.default = beans_daily_max
        
        await interaction.response.send_modal(modal)
        
    @group.command(name="gamba_setup", description="Opens a dialog to edit various gamba beans settings.")
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def gamba_setup(self, interaction: discord.Interaction):
        beans_gamba_cost = self.settings.get_beans_gamba_cost(interaction.guild_id)
        beans_gamba_cooldown = self.settings.get_beans_gamba_cooldown(interaction.guild_id)

        modal = BeansGambaSettingsModal(self.bot, self.settings)
        modal.beans_gamba_cost.default = str(beans_gamba_cost)
        modal.beans_gamba_cooldown.default = str(beans_gamba_cooldown)
        
        await interaction.response.send_modal(modal) 
    
    @group.command(name="add_channel", description='Enable beans commands for a channel.')
    @app_commands.describe(channel='The beans channel.')
    @app_commands.check(__has_permission)
    async def add_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        self.settings.add_beans_channel(interaction.guild_id, channel.id)
        await self.bot.command_response(self.__cog_name__, interaction, f'Added {channel.name} to beans channels.', args=[channel.name])
        
    @group.command(name="remove_channel", description='Disable beans commands for a channel.')
    @app_commands.describe(channel='Removes this channel from the beans channels.')
    @app_commands.check(__has_permission)
    async def remove_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        self.settings.remove_beans_channel(interaction.guild_id, channel.id)
        await self.bot.command_response(self.__cog_name__, interaction, f'Removed {channel.name} from beans channels.', args=[channel.name])
    
async def setup(bot):
    await bot.add_cog(Beans(bot))
