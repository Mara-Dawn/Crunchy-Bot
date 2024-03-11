import typing
import discord

from discord.ext import commands
from discord import app_commands
from BotLogger import BotLogger
from BotSettings import BotSettings
from MaraBot import MaraBot
from datalayer.Database import Database
from datalayer.Quote import Quote
from events.EventManager import EventManager

from view.ImageGenerator import ImageGenerator

class Quotes(commands.Cog):
    
    def __init__(self, bot: MaraBot):
        self.bot = bot
        self.logger: BotLogger = bot.logger
        self.settings: BotSettings = bot.settings
        self.database: Database = bot.database
        self.event_manager: EventManager = bot.event_manager
        
        self.ctx_menu = app_commands.ContextMenu(
            name='Quote',
            callback=self.quote_context_menu,
        )
        self.bot.tree.add_command(self.ctx_menu)
    
    async def quote_context_menu(self, interaction: discord.Interaction, message: discord.Message):
        guild_id = interaction.guild_id
        
        await interaction.response.defer()
        
        quote = Quote(
            message.created_at, 
            guild_id, 
            message.author.id, 
            message.author.display_name, 
            interaction.user.id, 
            message.id, 
            message.channel.id, 
            message.content
        )
        
        quote_id = self.database.log_quote(quote)
        
        self.event_manager.dispatch_quote_event(message.created_at, guild_id, quote_id)
        response = f'<@{message.author.id}> Your message {message.jump_url} was deemed quote worthy by <@{interaction.user.id}> and will be saved for the future.'
        await self.bot.response(self.__cog_name__, interaction, response, 'quote', interaction.user.display_name, message.author.display_name)
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.log("init",str(self.__cog_name__) + " loaded.", cog=self.__cog_name__)
        
    @app_commands.command(name="inspire", description='Get a random quote.')
    @app_commands.describe(
        user='Get quotes from this user.',
        )
    @app_commands.guild_only()
    async def inspire(self, interaction: discord.Interaction, user: typing.Optional[discord.Member] = None):
        await interaction.response.defer()
        
        image_generator = ImageGenerator(self.bot)
        if user is not None:
            quote = self.database.get_random_quote_by_user(interaction.guild_id, user.id)
        else:
            quote = self.database.get_random_quote(interaction.guild_id)
        
        image = image_generator.from_quote(quote)
        
        result_image = discord.File(image, "img.png")
        
        message_id = quote.get_message_id()
        channel_id = quote.get_channel_id()
        url = ''
        message = None
        if channel_id is None:
            for channel in interaction.guild.text_channels:
                try:
                    message = await channel.fetch_message(message_id)
                except discord.errors.NotFound as e:
                    continue
                except discord.errors.Forbidden as e:
                    pass
                if message is not None:
                    url = message.jump_url
                    self.database.fix_quote(quote, channel.id)
                    break
        else:
            
            try:
                message = await interaction.guild.get_channel(channel_id).fetch_message(message_id)
            except discord.errors.NotFound as e:
                pass
            except discord.errors.Forbidden as e:
                pass
            if message is not None:
                    url = message.jump_url
        
        await interaction.followup.send(f"Check this Quote from <@{quote.get_member()}>: {url}", files=[result_image], silent=True)

async def setup(bot):
    await bot.add_cog(Quotes(bot))