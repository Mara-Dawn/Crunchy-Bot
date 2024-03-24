import discord

from discord.ext import commands
from discord import app_commands
from BotLogger import BotLogger
from BotSettings import BotSettings
from BotUtil import Tenor
from MaraBot import MaraBot
from cogs.Jail import Jail
from datalayer.Database import Database
from datalayer.UserInteraction import UserInteraction
from events.EventManager import EventManager

class Interactions(commands.Cog):
    
    def __init__(self, bot: MaraBot):
        self.bot = bot
        self.logger: BotLogger = bot.logger
        self.settings: BotSettings = bot.settings
        self.database: Database = bot.database
        self.event_manager: EventManager = bot.event_manager
        
        self.ctx_menu = app_commands.ContextMenu(
            name='Slap',
            callback=self.slap_context_menu,
        )
        self.bot.tree.add_command(self.ctx_menu)
        
        self.ctx_menu = app_commands.ContextMenu(
            name='Pet',
            callback=self.pet_context_menu,
        )
        self.bot.tree.add_command(self.ctx_menu)
        
        self.ctx_menu = app_commands.ContextMenu(
            name='Fart',
            callback=self.fart_context_menu,
        )
        self.bot.tree.add_command(self.ctx_menu)
        
        self.ctx_menu = app_commands.ContextMenu(
            name='Slap',
            callback=self.slap_msg_context_menu,
        )
        self.bot.tree.add_command(self.ctx_menu)
        
        self.ctx_menu = app_commands.ContextMenu(
            name='Pet',
            callback=self.pet_msg_context_menu,
        )
        self.bot.tree.add_command(self.ctx_menu)
        
        self.ctx_menu = app_commands.ContextMenu(
            name='Fart',
            callback=self.fart_msg_context_menu,
        )
        self.bot.tree.add_command(self.ctx_menu)
    
    async def slap_context_menu(self, interaction: discord.Interaction, user: discord.Member):
        await self.__user_command_interaction(interaction, user, UserInteraction.SLAP)
    
    async def pet_context_menu(self, interaction: discord.Interaction, user: discord.Member):
        await self.__user_command_interaction(interaction, user, UserInteraction.PET)

    async def fart_context_menu(self, interaction: discord.Interaction, user: discord.Member):
        await self.__user_command_interaction(interaction, user, UserInteraction.FART)
    
    async def slap_msg_context_menu(self, interaction: discord.Interaction, message: discord.Message):
        await self.__user_command_interaction(interaction, message.author, UserInteraction.SLAP)
    
    async def pet_msg_context_menu(self, interaction: discord.Interaction, message: discord.Message):
        await self.__user_command_interaction(interaction, message.author, UserInteraction.PET)

    async def fart_msg_context_menu(self, interaction: discord.Interaction, message: discord.Message):
        await self.__user_command_interaction(interaction, message.author, UserInteraction.FART)
    
    def __get_response(self, type: UserInteraction, interaction: discord.Interaction, user: discord.Member) -> str:
        match type:
            case UserInteraction.SLAP:
                return f'<@{user.id}> was slapped by <@{interaction.user.id}>!'
            case UserInteraction.PET:
                return f'<@{user.id}> recieved pets from <@{interaction.user.id}>!'
            case UserInteraction.FART:
                return f'<@{user.id}> was farted on by <@{interaction.user.id}>!'
    
    async def __get_response_embed(self, type: UserInteraction, interaction: discord.Interaction, user: discord.Member) -> str:
        search = ''
        match type:
            case UserInteraction.SLAP:
                search = 'bitchslap'
            case UserInteraction.PET:
                search = f'headpats'
            case UserInteraction.FART:
                search = f'fart'
        
        token = open(self.bot.TENOR_TOKEN_FILE,"r").readline()
        g = Tenor(token=token)
        gif = await g.random(tag=search)
        embed = discord.Embed(color=discord.Colour.purple())
        embed.set_image(url=gif)
        
        return embed
    
    async def __user_command_interaction(self, interaction: discord.Interaction, user: discord.Member, command_type: UserInteraction):
        command = interaction.command
        guild_id = interaction.guild_id
        invoker = interaction.user
        
        await interaction.response.defer()
                
        self.event_manager.dispatch_interaction_event(interaction.created_at, guild_id, command_type, invoker.id, user.id)
        
        log_message = f'{interaction.user.name} used command `{command.name}` on {user.name}.'
        self.logger.log(interaction.guild_id, log_message, cog=self.__cog_name__)
        
        
        embed = await self.__get_response_embed(command_type, interaction, user)
        response = self.__get_response(command_type, interaction, user)
        
        jail_cog: Jail = self.bot.get_cog('Jail')
        response += await jail_cog.user_command_interaction(interaction, user, command_type)
        
        await interaction.channel.send(response)
        await interaction.followup.send(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.log("init",str(self.__cog_name__) + " loaded.", cog=self.__cog_name__)
    
    @app_commands.command(name="slap", description="Slap someone.")
    @app_commands.describe(
        user='Slap this bitch.',
        )
    @app_commands.guild_only()
    @app_commands.checks.cooldown(1, 10)
    async def slap(self, interaction: discord.Interaction, user: discord.Member):
        await self.__user_command_interaction(interaction, user, UserInteraction.SLAP)
    
    @app_commands.command(name="pet", description='Give someone a pat.')
    @app_commands.describe(
        user='Give them a pat.',
        )
    @app_commands.guild_only()
    @app_commands.checks.cooldown(1, 10)
    async def pet(self, interaction: discord.Interaction, user: discord.Member):
        await self.__user_command_interaction(interaction, user, UserInteraction.PET)

    @app_commands.command(name="fart", description='Fart on someone.')
    @app_commands.describe(
        user='Fart on this user.',
        )
    @app_commands.guild_only()
    @app_commands.checks.cooldown(1, 10)
    async def fart(self, interaction: discord.Interaction, user: discord.Member):
        await self.__user_command_interaction(interaction, user, UserInteraction.FART)
                
async def setup(bot):
    await bot.add_cog(Interactions(bot))
