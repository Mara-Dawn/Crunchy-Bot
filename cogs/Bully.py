import typing
import discord

from discord.ext import commands
from BotLogger import BotLogger
from BotSettings import BotSettings
from CrunchyBot import CrunchyBot
from RoleManager import RoleManager
from datalayer.Database import Database
from datalayer.ItemTrigger import ItemTrigger
from events.EventManager import EventManager
from shop.ItemManager import ItemManager
from shop.ItemType import ItemType

class Bully(commands.Cog):
    
    def __init__(self, bot: CrunchyBot):
        self.bot = bot
        self.logger: BotLogger = bot.logger
        self.settings: BotSettings = bot.settings
        self.database: Database = bot.database
        self.role_manager: RoleManager = bot.role_manager
        self.event_manager: EventManager = bot.event_manager
        self.item_manager: ItemManager = bot.item_manager

    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.log("init",str(self.__cog_name__) + " loaded.", cog=self.__cog_name__)
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id == self.bot.user.id:
            return
        
        if message.author.bot:
            return
        
        if not message.guild:
            return
        
        guild_id = message.guild.id
        
        if not self.settings.get_beans_enabled(guild_id):
            self.logger.log(guild_id, f'Beans module disabled.', cog=self.__cog_name__)
            return
        
        inventories = self.database.get_inventories_by_guild(guild_id)
        user_items = await self.item_manager.get_guild_items_activated(guild_id, inventories, ItemTrigger.USER_MESSAGE)
        
        for user_id, items in user_items.items():
            for item in items:
                match item.get_type():
                    case ItemType.REACTION_SPAM:
                        
                        target_id, emoji = self.database.get_bully_react(guild_id, user_id)
                        
                        if message.author.id != target_id:
                            continue
                        
                        if emoji is None:
                            continue
                        
                        current_message = await message.channel.fetch_message(message.id)
                        if emoji in [x.emoji for x in current_message.reactions]:
                            continue
                        
                        await message.add_reaction(emoji)
                        
                        await item.use(
                            self.role_manager,
                            self.event_manager,
                            guild_id,
                            user_id,
                            1
                        )
                        
                    case _ :
                        continue
            
async def setup(bot):
    await bot.add_cog(Bully(bot))