import discord

from discord.ext import commands
from BotLogger import BotLogger
from BotSettings import BotSettings
from datalayer.Database import Database
from events.EventManager import EventManager

class MaraBot(commands.Bot):
    
    DB_FILE = "database.sqlite"
    LOG_FILE = "./log/marabot.log"
    TENOR_TOKEN_FILE = 'tenor.txt'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def setup_hook(self) -> None:
        self.logger = BotLogger(self, self.LOG_FILE)
        self.database = Database(self.logger, self.DB_FILE)
        self.settings = BotSettings(self,self.database, self.logger)
        self.event_manager = EventManager(self, self.settings, self.database, self.logger)
        await self.load_extension("cogs.Police")
        await self.load_extension("cogs.Jail")
        await self.load_extension("cogs.Interactions")
        await self.load_extension("cogs.Statistics")
        await self.load_extension("cogs.Quotes")
        
    async def on_guild_join(self, guild):
        self.logger.log(guild.id,  "new guild registered.")

    async def on_guild_remove(self, guild):
        self.logger.log(guild.id, "guild removed.")
    
    async def command_response(self, module: str,  interaction: discord.Interaction, message: str, *args) -> None:
        return await self.response(module, interaction, message, interaction.command.name, *args)
    
    async def response(self, module: str,  interaction: discord.Interaction, message: str, command: str, *args) -> None:
        log_message = f'{interaction.user.name} used command `{command}`.'
        
        if len(args) > 0: 
            log_message += " Arguments: " + ", ".join([str(x) for x in args])
                
        self.logger.log(interaction.guild_id, log_message, cog=module)
        
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(message, ephemeral=True) 
            else:
                await interaction.followup.send(message, ephemeral=True) 
        except discord.errors.InteractionResponded:
            await interaction.followup.send(message, ephemeral=True) 
    