import discord

from discord.ext import commands
from BotLogger import BotLogger
from BotSettings import BotSettings
from datalayer.Database import Database
from events.BotEventManager import BotEventManager

class MaraBot(commands.Bot):

    SETTINGS_FILE = "settings.json"
    DB_FILE = "database.sqlite"
    LOG_FILE = "marabot.log"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def setup_hook(self) -> None:
        
        self.logger = BotLogger(self, self.LOG_FILE)
        self.database = Database(self.logger, self.DB_FILE)
        self.settings = BotSettings(self,self.database, self.logger, self.SETTINGS_FILE)
        self.event_manager = BotEventManager(self, self.settings, self.database, self.logger)
        await self.load_extension("cogs.Police")
        await self.load_extension("cogs.Jail")
        await self.load_extension("cogs.Statistics")
        
    async def on_guild_join(self, guild):

        self.logger.log(guild.id,  "new guild registered.")

    async def on_guild_remove(self, guild):

        self.logger.log(guild.id, "guild removed.")
        
    async def command_response(self, module: str,  interaction: discord.Interaction, message: str, *args) -> None:
        
        log_message = f'{interaction.user.name} used command `{interaction.command.name}`.'
        
        if len(args) > 0: 
            log_message += " Arguments: " + ", ".join([str(x) for x in args])
                
        self.logger.log(interaction.guild_id, log_message, cog=module)
        await interaction.response.send_message(message, ephemeral=True)
    
    async def modal_response(self, module: str,  interaction: discord.Interaction, message: str, command: str, *args) -> None:
        
        log_message = f'{interaction.user.name} used command `{command}`.'
        
        if len(args) > 0: 
            log_message += " Arguments: " + ", ".join([str(x) for x in args])
                
        self.logger.log(interaction.guild_id, log_message, cog=module)
        await interaction.response.send_message(message, ephemeral=True)