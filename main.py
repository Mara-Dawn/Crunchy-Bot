import discord
from discord.ext import commands

from MaraBot import MaraBot

TOKEN_FILE = 'key.txt'

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.emojis_and_stickers = True
intents.reactions = True
intents.emojis_and_stickers = True

activity = discord.Activity(type=discord.ActivityType.watching, name="this monkey zoo")

bot = MaraBot( intents=intents, activity=activity)

@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
    if isinstance(error, commands.CommandOnCooldown):
        return await ctx.respond(f"Command is currently on cooldown! Try again in **{error.retry_after:.2f}** seconds!", ephemeral=True)
    elif isinstance(error, commands.MissingPermissions):
        return await ctx.respond(f"You're missing permissions to use that", ephemeral=True)
    elif isinstance(error, commands.errors.CheckFailure):
        return await ctx.respond(f"You're missing permissions to use that", ephemeral=True)
    else:
        raise error

token = open(TOKEN_FILE,"r").readline()
bot.run(token)