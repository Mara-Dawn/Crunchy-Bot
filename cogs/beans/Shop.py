import datetime
import discord

from discord.ext import commands, tasks
from discord import app_commands
from typing import Literal
from BotLogger import BotLogger
from BotSettings import BotSettings
from CrunchyBot import CrunchyBot
from datalayer.Database import Database
from datalayer.ItemTrigger import ItemTrigger
from events.EventManager import EventManager
from shop.ItemManager import ItemManager
from shop.ItemType import ItemType
from view.InventoryEmbed import InventoryEmbed
from view.ShopMenu import ShopMenu
from view.ShopEmbed import ShopEmbed

class Shop(commands.Cog):
    
    def __init__(self, bot: CrunchyBot):
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
        
        if interaction.channel_id not in self.settings.get_beans_channels(guild_id):
            await self.bot.command_response(self.__cog_name__, interaction, f'Shop commands cannot be used in this channel.')
            return False
        
        return True

    @commands.Cog.listener()
    async def on_ready(self):
        self.daily_collection_task.start()
        self.logger.log("init",str(self.__cog_name__) + " loaded.", cog=self.__cog_name__)
    
    @tasks.loop(time=datetime.time(hour=0))
    async def daily_collection_task(self):
        self.logger.log("sys", f'Daily Item Check started.', cog=self.__cog_name__)
        
        for guild in self.bot.guilds:
            if not self.settings.get_beans_enabled(guild.id):
                self.logger.log("sys", f'Beans module disabled.', cog=self.__cog_name__)
                return
            
            inventories = self.database.get_inventories_by_guild(guild.id)
            await self.item_manager.use_items(guild.id, inventories, ItemTrigger.DAILY)
            
    
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
        items = self.item_manager.get_items(interaction.guild_id)
        
        embed = ShopEmbed(self.bot, interaction, items)
        view = ShopMenu(self.bot, interaction, items)
        
        message = await interaction.followup.send("",embed=embed, view=view, files=[shop_img, police_img])
        view.set_message(message)
        
    @app_commands.command(name="inventory", description='See the items you have bought from the beans shop.')
    @app_commands.guild_only()
    async def inventory(self, interaction: discord.Interaction):
        if not await self.__check_enabled(interaction):
            return 
        
        log_message = f'{interaction.user.name} used command `{interaction.command.name}`.'
        self.logger.log(interaction.guild_id, log_message, cog=self.__cog_name__)
        await interaction.response.defer(ephemeral=True)
        
        police_img = discord.File("./img/police.png", "police.png")
        
        member_id = interaction.user.id
        guild_id = interaction.guild_id
        inventory = self.database.get_inventory_by_user(guild_id, member_id)
        user_balance = self.database.get_member_beans(guild_id, member_id)
        embed = InventoryEmbed(self.bot, interaction, inventory, user_balance)
        
        await interaction.followup.send("",embed=embed, files=[police_img])
    
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