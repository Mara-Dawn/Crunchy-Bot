import discord

from discord.ext import commands
from discord import app_commands
from BotLogger import BotLogger
from BotSettings import BotSettings
from MaraBot import MaraBot
from datalayer.Database import Database
from datalayer.Quote import Quote
from events.BotEventManager import BotEventManager

class Quotes(commands.Cog):
    
    def __init__(self, bot: MaraBot):
        self.bot = bot
        
        self.logger: BotLogger = bot.logger
        self.settings: BotSettings = bot.settings
        self.database: Database = bot.database
        self.event_manager: BotEventManager = bot.event_manager
        
        self.ctx_menu = app_commands.ContextMenu(
            name='Quote',
            callback=self.quote_menu,
        )
        self.bot.tree.add_command(self.ctx_menu)
    
    async def quote_menu(self, interaction: discord.Interaction, message: discord.Message):
        
        guild_id = interaction.guild_id
        
        await interaction.response.defer()
        
        quote = Quote(
            message.created_at, 
            guild_id, 
            message.author.id, 
            message.author.display_name, 
            interaction.user.id, 
            message.id, 
            message.content
        )
        
        quote_id = self.database.log_quote(quote)
        
        self.event_manager.dispatch_quote_event(message.created_at, guild_id, quote_id)
        response = 'Quote was sucessfully saved.'
        await self.bot.response(self.__cog_name__, interaction, response, 'quote', interaction.user.display_name, message.author.display_name)
    
    @commands.Cog.listener()
    async def on_ready(self):
        
        self.logger.log("init",str(self.__cog_name__) + " loaded.", cog=self.__cog_name__)
    
async def setup(bot):
    await bot.add_cog(Quotes(bot))
