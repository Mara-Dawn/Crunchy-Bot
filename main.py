import discord

from discord.ext import commands
from discord import app_commands
from MaraBot import MaraBot

TOKEN_FILE = 'key.txt'

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.emojis_and_stickers = True
intents.reactions = True
intents.emojis_and_stickers = True

bot = MaraBot(command_prefix="/", intents=intents)

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