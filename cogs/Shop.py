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
from shop.ItemManager import ItemManager
from shop.ItemType import ItemType
from view.BeansDailySettingsModal import BeansDailySettingsModal
from view.BeansGambaSettingsModal import BeansGambaSettingsModal
from view.ShopMenu import ShopMenu
from view.ShopEmbed import ShopEmbed

class Shop(commands.Cog):
    
    def __init__(self, bot: MaraBot):
        self.bot = bot
        self.logger: BotLogger = bot.logger
        self.settings: BotSettings = bot.settings
        self.database: Database = bot.database
        self.event_manager: EventManager = bot.event_manager
        self.item_manager: ItemManager = bot.item_manager

    async def __has_permission(interaction: discord.Interaction) -> bool:
        author_id = 90043934247501824
        return interaction.user.id == author_id or interaction.user.guild_permissions.administrator

    async def __check_enabled(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        if not self.settings.get_shop_enabled(guild_id):
            await self.bot.command_response(self.__cog_name__, interaction, f'Beans shop module is currently disabled.')
            return False
        return True

    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.log("init",str(self.__cog_name__) + " loaded.", cog=self.__cog_name__)
    
    @app_commands.command(name="shop", description='Buy cool stuff with your beans.')
    @app_commands.guild_only()
    async def shop(self, interaction: discord.Interaction):
        if not await self.__check_enabled(interaction):
            return 
        
        log_message = f'{interaction.user.name} used command `{interaction.command.name}`.'
        self.logger.log(interaction.guild_id, log_message, cog=self.__cog_name__)
        await interaction.response.defer()
        
        shop_img = discord.File("./img/shop.png", "shop.png")
        police_img = discord.File("./img/police.png", "police.png")
        
        embed = ShopEmbed(self.bot, interaction)
        view = ShopMenu(self.bot, interaction)
        
        await interaction.followup.send("",embed=embed, view=view, files=[shop_img, police_img])
    
    group = app_commands.Group(name="beansshop", description="Subcommands for the Beans Shop module.")
    
    @group.command(name="settings", description="Overview of all beans shop related settings and their current value.")
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def get_settings(self, interaction: discord.Interaction):
        output = self.settings.get_settings_string(interaction.guild_id, BotSettings.SHOP_SUBSETTINGS_KEY)
        await self.bot.command_response(self.__cog_name__, interaction, output)
    
    @group.command(name="toggle", description="Enable or disable the entire beans shop module.")
    @app_commands.describe(enabled='Turns the beans shop module on or off.')
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def set_toggle(self, interaction: discord.Interaction, enabled: Literal['on', 'off']):
        self.settings.set_shop_enabled(interaction.guild_id, enabled == "on")
        await self.bot.command_response(self.__cog_name__, interaction, f'Beans shop module was turned {enabled}.', args=[enabled])
      
    @group.command(name="price", description="Adjust item prices for the beans shop.")
    @app_commands.describe(
        item='The item you are about to change.',
        amount='The new price for the specified item.',
    )
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def price(self, interaction: discord.Interaction, item: ItemType, amount: app_commands.Range[int, 1]):
        self.settings.set_shop_item_price(interaction.guild_id, item.value, amount)
        await self.bot.command_response(self.__cog_name__, interaction, f'Price for {item.value} was set to {amount} beans.', args=[item, amount])
    
async def setup(bot):
    await bot.add_cog(Shop(bot))