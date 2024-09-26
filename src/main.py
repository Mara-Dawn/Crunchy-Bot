import discord
from discord import app_commands

from bot import CrunchyBot
from error import ErrorHandler

TOKEN_FILE = "key.txt"

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.emojis_and_stickers = True
intents.reactions = True

activity = discord.Activity(type=discord.ActivityType.playing, name="with your beans")

bot = CrunchyBot(
    command_prefix="/", intents=intents, activity=activity, help_command=None
)
error_handler = ErrorHandler(bot)


async def on_tree_error(
    interaction: discord.Interaction, error: app_commands.AppCommandError
) -> None:
    await error_handler.on_tree_error(interaction, error)


bot.tree.on_error = on_tree_error

with open(TOKEN_FILE) as file:
    token = file.readline()
    bot.run(token)
