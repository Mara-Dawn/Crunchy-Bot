import discord

from discord.ext import commands
from discord import app_commands
from typing import Dict, Literal
from BotLogger import BotLogger
from BotSettings import BotSettings
from MaraBot import MaraBot
from datalayer.Database import Database
from datalayer.UserInteraction import UserInteraction
from events.BotEventManager import BotEventManager

class Statistics(commands.Cog):
    
    def __init__(self, bot: MaraBot):
        self.bot = bot
        
        self.logger: BotLogger = bot.logger
        self.settings: BotSettings = bot.settings
        self.database: Database = bot.database
        self.event_manager: BotEventManager = bot.event_manager
        
    
    async def __has_permission(interaction: discord.Interaction) -> bool:
        
        author_id = 90043934247501824
        return interaction.user.id == author_id or interaction.user.guild_permissions.administrator
    
    async def __has_mod_permission(self, interaction: discord.Interaction) -> bool:
        
        author_id = 90043934247501824
        roles = self.settings.get_jail_mod_roles(interaction.guild_id)
        is_mod = bool(set([x.id for x in interaction.user.roles]).intersection(roles))
        return interaction.user.id == author_id or interaction.user.guild_permissions.administrator or is_mod
    
                
async def setup(bot):
    await bot.add_cog(Statistics(bot))
