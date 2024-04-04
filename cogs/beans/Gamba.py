import asyncio
import datetime
import random
import typing
import discord

from discord.ext import commands
from discord import app_commands
from typing import *
from BotLogger import BotLogger
from BotSettings import BotSettings
from CrunchyBot import CrunchyBot
from RoleManager import RoleManager
from datalayer.Database import Database
from events.BeansEventType import BeansEventType
from events.EventManager import EventManager
from shop.ItemManager import ItemManager
from view.SettingsModal import SettingsModal

class Gamba(commands.Cog):
    
    def __init__(self, bot: CrunchyBot):
        self.bot = bot
        self.logger: BotLogger = bot.logger
        self.settings: BotSettings = bot.settings
        self.database: Database = bot.database
        self.event_manager: EventManager = bot.event_manager
        self.role_manager: RoleManager = bot.role_manager
        self.item_manager: ItemManager = bot.item_manager

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
        
        stunned_remaining = self.event_manager.get_stunned_remaining(guild_id, interaction.user.id)
        if stunned_remaining > 0:
            timestamp_now = int(datetime.datetime.now().timestamp())
            remaining = int(timestamp_now+stunned_remaining)
            await self.bot.command_response(self.__cog_name__, interaction, f'You are currently stunned from a bat attack. Try again <t:{remaining}:R>')
            return False
        
        return True
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.log("init",str(self.__cog_name__) + " loaded.", cog=self.__cog_name__)

    @app_commands.command(name="gamba", description='Gamba away your beans.')
    @app_commands.guild_only()
    async def gamba(self, interaction: discord.Interaction, amount: typing.Optional[int] = None):
        if not await self.__check_enabled(interaction):
            return 
        
        guild_id = interaction.guild_id
        user_id = interaction.user.id
        beans_gamba_min = self.settings.get_beans_gamba_min(guild_id)
        beans_gamba_max = self.settings.get_beans_gamba_max(guild_id)
        default_cooldown = self.settings.get_beans_gamba_cooldown(guild_id)
        timestamp_now = int(datetime.datetime.now().timestamp())

        if amount is not None:
            if not (beans_gamba_min <= amount and amount <= beans_gamba_max):
                await self.bot.command_response(self.__cog_name__, interaction, f'Between `🅱️{beans_gamba_min}` and `🅱️{beans_gamba_max}` you fucking monkey.', ephemeral=False)
                return 
            
        await interaction.response.defer()

        default_amount = self.settings.get_beans_gamba_cost(guild_id)
        
        if amount is None:
            amount = default_amount

        current_balance = self.database.get_member_beans(guild_id, user_id)
        
        if current_balance < amount:
            await self.bot.command_response(self.__cog_name__, interaction, f'You\'re out of beans, idiot.', ephemeral=False)
            return
        
        last_gamba_cost_event = self.database.get_last_beans_event(guild_id, user_id, BeansEventType.GAMBA_COST)
        last_gamba_payout_event = self.database.get_last_beans_event(guild_id, user_id, BeansEventType.GAMBA_PAYOUT)
        
        if last_gamba_cost_event is not None: 
        
            current_date = datetime.datetime.now()
            last_gamba_beans_date = last_gamba_cost_event.get_datetime()
            
            delta = current_date - last_gamba_beans_date
            delta_seconds = delta.total_seconds()
            
            last_gamba_amount = abs(last_gamba_cost_event.get_value())
            cooldown = default_cooldown 
            
            if last_gamba_payout_event.get_value() != 0:
                #only go on cooldown when previous gamba was a win
                cooldown = default_cooldown * (last_gamba_amount / default_amount) 

            if delta_seconds <= cooldown:
                remaining = cooldown - delta_seconds
                cooldowntimer = int(timestamp_now + remaining)
                
                await self.bot.command_response(self.__cog_name__, interaction, f'Gamba is on cooldown. Try again in <t:{cooldowntimer}:R>.', ephemeral=False)
                message = await interaction.original_response()
                channel_id = message.channel.id
                message_id = message.id
                
                await asyncio.sleep(remaining)
                
                message = await self.bot.get_guild(guild_id).get_channel(channel_id).fetch_message(message_id)
                await message.delete()
                return
        
        self.event_manager.dispatch_beans_event(
            datetime.datetime.now(), 
            guild_id, 
            BeansEventType.GAMBA_COST, 
            user_id,
            -amount
        )
        
        response = f'You paid `🅱️{amount}` beans to gamba.'
        
        display_values = [
            '\n**0x**',
            '\n**2x**🎲',
            '\n**3x**🎲🎲',
            '\n**10x**🎲🎲🎲',
            '\n**100x**🎲🎲🎲🎲'
        ]
        
        payout = 0
        
        loss = 0.50 
        doubling = 0.33 
        tripling = 0.15
        tenfold = 0.019 
        jackpot = 0.001
        
        # (0.33*2)+(0.15*3)+(0.019*10)+(0.001*100)
        result = random.random()
        
        if result <= loss:
            final_display = 0
            final = f'\nYou lost. It is what it is.'
        elif result > loss and result <= (loss+doubling):
            final_display = 1
            payout = amount * 2
            final = f'\nYou won! Your payout is `🅱️{payout}` beans.'
        elif result > (loss+doubling) and result <= (loss+doubling+tripling):
            final_display = 2
            payout = amount * 3
            final = f'\nWow you got lucky! Your payout is `🅱️{payout}` beans.'
        elif result > (loss+doubling+tripling) and result <= (1-jackpot):
            final_display = 3
            payout = amount * 10
            final = f'\n**BIG WIN!** Your payout is `🅱️{payout}` beans.'
        elif result > (1-jackpot) and result <= 1:
            final_display = 4
            payout = amount * 100
            final = f'\n**JACKPOT!!!** Your payout is `🅱️{payout}` beans.'
        
        display = display_values[0]
        await self.bot.command_response(self.__cog_name__, interaction, response, ephemeral=False)
        
        message = await interaction.original_response()
        i = 0
        current = i
        while i <= 10 or current != final_display:
            current = i % len(display_values)
            display = display_values[current]
            await asyncio.sleep((1/20)*i)
            await message.edit(content=response+display)
            i += 1
        
        today = datetime.datetime.now().date()
        today_timestamp = datetime.datetime(year=today.year, month=today.month, day=today.day).timestamp()
        
        user_daily_gamba_count = self.database.get_beans_daily_gamba_count(guild_id, user_id, BeansEventType.GAMBA_COST, default_amount, today_timestamp)
        beans_bonus_amount = 0
        match user_daily_gamba_count:
            case 10:
                beans_bonus_amount = self.settings.get_beans_bonus_amount_10(interaction.guild_id)
            case 25:
                beans_bonus_amount = self.settings.get_beans_bonus_amount_25(interaction.guild_id)
        
        if beans_bonus_amount > 0:
            final += f'\n🎉 You reached **{user_daily_gamba_count}** gambas for today! Enjoy these bonus beans `🅱️{beans_bonus_amount}` 🎉'
            self.event_manager.dispatch_beans_event(
                datetime.datetime.now(), 
                guild_id, 
                BeansEventType.BONUS_PAYOUT, 
                user_id,
                beans_bonus_amount
            )
        
        self.event_manager.dispatch_beans_event(
            datetime.datetime.now(), 
            guild_id, 
            BeansEventType.GAMBA_PAYOUT, 
            user_id,
            payout
        )
        cooldowntimer = int(default_cooldown*amount/default_amount)
        if payout == 0:
            cooldowntimer = int(default_cooldown)
        remaining = int(timestamp_now+cooldowntimer)
        timer =f'\nYou can gamble again <t:{remaining}:R>.'
        await message.edit(content=response+display+final+timer)
        channel_id = message.channel.id
        message_id = message.id
        await asyncio.sleep(max(0,cooldowntimer-10))
        message = await self.bot.get_guild(guild_id).get_channel(channel_id).fetch_message(message_id)
        await message.edit(content=response+display+final)
    
    @app_commands.command(name="gamba_setup", description="Opens a dialog to edit various gamba beans settings.")
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def gamba_setup(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        modal = SettingsModal(self.bot, self.settings, self.__cog_name__, interaction.command.name, "Settings for Gamba related Features")
        
        modal.add_field(guild_id, BotSettings.BEANS_SUBSETTINGS_KEY, BotSettings.BEANS_GAMBA_DEFAULT_KEY, int)
        modal.add_field(guild_id, BotSettings.BEANS_SUBSETTINGS_KEY, BotSettings.BEANS_GAMBA_COOLDOWN_KEY, int)
        modal.add_field(guild_id, BotSettings.BEANS_SUBSETTINGS_KEY, BotSettings.BEANS_GAMBA_MIN_KEY, int)
        modal.add_field(guild_id, BotSettings.BEANS_SUBSETTINGS_KEY, BotSettings.BEANS_GAMBA_MAX_KEY, int)
        
        modal.add_constraint([BotSettings.BEANS_GAMBA_MIN_KEY, BotSettings.BEANS_GAMBA_MAX_KEY], lambda a,b: a <= b , 'Gamba minimum must be smaller than gamba maximum.')
        
        await interaction.response.send_modal(modal) 
    
async def setup(bot):
    await bot.add_cog(Gamba(bot))
