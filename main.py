
import discord

from discord.ext import commands
from logger import BotLogger
from settings import BotSettings
from userlist import UserList
from cogs.Police import Police

TOKEN_FILE = 'key.txt'
AUTHOR_ID = 90043934247501824

class MommyBot(commands.Bot):

    SETTINGS_FILE = "settings.json"
    LOG_FILE = "mommybot.log"

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.logger = BotLogger(self, self.LOG_FILE)
        self.settings = BotSettings(self.logger, self.SETTINGS_FILE)

    async def setup_hook(self) -> None:
        
        await self.load_extension("cogs.Police")

    async def on_guild_join(self, guild):

        self.logger.log(guild.id,  "new guild registered.")
        self.settings.add_guild(guild.id)

    async def on_guild_remove(self, guild):

        self.settings.remove_guild(guild.id)
        self.logger.log(guild.id, "guild removed.")

    async def on_message(self, message):
        await self.process_commands(message)



intents = discord.Intents.default()
intents.message_content = True

bot = MommyBot(command_prefix="/", intents=intents)

token = open(TOKEN_FILE,"r").readline()
bot.run(token)


#Set-ExecutionPolicy Unrestricted -Scope Process
