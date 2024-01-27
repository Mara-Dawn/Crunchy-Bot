import pathlib
import typing
import discord

from discord.ext import commands
from discord import app_commands
from BotLogger import BotLogger
from BotSettings import BotSettings
from MaraBot import MaraBot
from datalayer.Database import Database
from datalayer.Quote import Quote
from events.BotEventManager import BotEventManager
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

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
        
    # @app_commands.command(name="inspire", description='Get a random quote.')
    # @app_commands.describe(
    #     user='Get quotes from this user.',
    #     )
    # @app_commands.guild_only()
    # async def inspire(self, interaction: discord.Interaction, user: typing.Optional[discord.Member] = None):
    #     await interaction.response.defer()
        
    #     pathlib.Path('./tmp/').mkdir(exist_ok=True) 
    #     I=Image.open("./img/jail.png")
    #     Im = ImageDraw.Draw(I)
    #     mf = ImageFont.truetype('./fonts/Beautiful Heart.ttf', 250)
    #     # Add Text to an
    #     Im.text((15,15), "Ayy Lmao", (255,0,0), font=mf)
    #     I.save("./tmp/m.png")
    #     test_img = discord.File("./tmp/m.png", "m.png")
    #     await interaction.followup.send("Test", files=[test_img])
            
    
async def setup(bot):
    await bot.add_cog(Quotes(bot))
