from typing import Any, List
import discord

from discord.ext import commands
from discord import app_commands
from BotLogger import BotLogger
from BotSettings import BotSettings
from RoleManager import RoleManager
from datalayer.Database import Database
from events.EventManager import EventManager
from shop.ItemManager import ItemManager

class CrunchyBot(commands.Bot):
    
    DB_FILE = "database.sqlite"
    LOG_FILE = "./log/marabot.log"
    TENOR_TOKEN_FILE = 'tenor.txt'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def setup_hook(self) -> None:
        self.logger = BotLogger(self, self.LOG_FILE)
        self.database = Database(self.logger, self.DB_FILE)
        self.settings = BotSettings(self,self.database, self.logger)
        self.role_manager = RoleManager(self, self.settings, self.database, self.logger)
        self.event_manager = EventManager(self, self.settings, self.database, self.logger)
        self.item_manager = ItemManager(self, self.settings, self.database, self.event_manager, self.role_manager, self.logger)
        await self.load_extension("cogs.Police")
        await self.load_extension("cogs.Jail")
        await self.load_extension("cogs.Interactions")
        await self.load_extension("cogs.Statistics")
        await self.load_extension("cogs.Quotes")
        await self.load_extension("cogs.beans.Shop")
        await self.load_extension("cogs.beans.Gamba")
        await self.load_extension("cogs.beans.Beans")
        
    async def on_guild_join(self, guild):
        self.logger.log(guild.id,  "new guild registered.")

    async def on_guild_remove(self, guild):
        self.logger.log(guild.id, "guild removed.")
    
    async def command_response(self, module: str,  interaction: discord.Interaction, message: str, args: List[Any] = [], ephemeral: bool = True) -> None:
        return await self.response(module, interaction, message, interaction.command.name, args, ephemeral)
    
    async def response(self, module: str,  interaction: discord.Interaction, message: str, command: str, args: List[Any] = [], ephemeral: bool = True) -> None:
        log_message = f'{interaction.user.name} used command `{command}`.'
        
        if len(args) > 0:
            log_message += " Arguments: " + ", ".join([str(x) for x in args])
                
        self.logger.log(interaction.guild_id, log_message, cog=module)
        allowed_mentions = discord.AllowedMentions(roles = True)
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(message, ephemeral=ephemeral, allowed_mentions=allowed_mentions) 
            else:
                await interaction.followup.send(message, ephemeral=ephemeral, allowed_mentions=allowed_mentions) 
        except discord.errors.InteractionResponded:
            await interaction.followup.send(message, ephemeral=ephemeral, allowed_mentions=allowed_mentions) 
    