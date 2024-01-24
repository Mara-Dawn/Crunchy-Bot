from typing import Literal
import discord

from BotLogger import BotLogger
from BotSettings import BotSettings
from datalayer.Database import Database
from events.BotEventManager import BotEventManager
from discord.commands import SlashCommandGroup

class MaraBot(discord.Bot):

    SETTINGS_FILE = "settings.json"
    DB_FILE = "database.sqlite"
    LOG_FILE = "marabot.log"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.logger = BotLogger(self, self.LOG_FILE)
        self.database = Database(self.logger, self.DB_FILE)
        self.settings = BotSettings(self,self.database, self.logger, self.SETTINGS_FILE)
        self.event_manager = BotEventManager(self, self.settings, self.database, self.logger)
        
        self.load_extension("cogs.Police")
        self.load_extension("cogs.Jail")
     
    async def on_ready(self):
        pass# await self.sync_commands(guild_ids=[x.id for x in self.guilds])
     
    async def on_guild_join(self, guild):

        self.logger.log(guild.id,  "new guild registered.")
    
    async def on_guild_remove(self, guild):

        self.logger.log(guild.id, "guild removed.")

    async def command_response(self, module: str,  ctx: discord.ApplicationContext, message: str, *args) -> None:
        
        log_message = f'{ctx.author.name} used command `{ctx.command.name}`.'
        
        if len(args) > 0: 
            log_message += " Arguments: " + ", ".join([str(x) for x in args])
                
        self.logger.log(ctx.guild_id, log_message, cog=module)
        await ctx.respond(message, ephemeral=True)
