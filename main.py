
import discord

from discord.ext import commands
from discord import app_commands
from logger import BotLogger
from BotSettings import BotSettings
from datalayer.UserList import UserList
from cogs.Police import Police

TOKEN_FILE = 'key.txt'

class MommyBot(commands.Bot):

    SETTINGS_FILE = "settings.json"
    LOG_FILE = "mommybot.log"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def setup_hook(self) -> None:
        self.logger = BotLogger(self, self.LOG_FILE)
        self.settings = BotSettings(self, self.logger, self.SETTINGS_FILE)
        await self.load_extension("cogs.Police")

    async def on_guild_join(self, guild):

        self.logger.log(guild.id,  "new guild registered.")

    async def on_guild_remove(self, guild):

        self.logger.log(guild.id, "guild removed.")



intents = discord.Intents.default()
intents.message_content = True

bot = MommyBot(command_prefix="/", intents=intents)

async def on_tree_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        return await interaction.response.send_message(f"Command is currently on cooldown! Try again in **{error.retry_after:.2f}** seconds!", ephemeral=True)
    elif isinstance(error, app_commands.MissingPermissions):
        return await interaction.response.send_message(f"You're missing permissions to use that", ephemeral=True)
    elif isinstance(error, app_commands.errors.CheckFailure):
        return await interaction.response.send_message(f"You're missing permissions to use that", ephemeral=True)
    else:
        raise error



bot.tree.on_error = on_tree_error

token = open(TOKEN_FILE,"r").readline()
bot.run(token)


#Set-ExecutionPolicy Unrestricted -Scope Process
