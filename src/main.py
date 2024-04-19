import discord
from bot import CrunchyBot
from discord import app_commands

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


async def on_tree_error(
    interaction: discord.Interaction, error: app_commands.AppCommandError
) -> None:
    if isinstance(error, app_commands.CommandOnCooldown):
        return await interaction.response.send_message(
            f"Command is currently on cooldown! Try again in **{error.retry_after:.2f}** seconds!",
            ephemeral=True,
        )
    elif isinstance(
        error, app_commands.MissingPermissions | app_commands.errors.CheckFailure
    ):
        return await interaction.response.send_message(
            "You're missing permissions to use that", ephemeral=True
        )
    else:
        error_msg = "Oops! Something went wrong. Consider contacting a staff member to fix the issue."
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(error_msg, ephemeral=True)
            else:
                await interaction.followup.send(error_msg, ephemeral=True)
        except discord.errors.InteractionResponded:
            await interaction.followup.send(error_msg, ephemeral=True)

        raise error


bot.tree.on_error = on_tree_error

with open(TOKEN_FILE) as file:
    token = file.readline()
    bot.run(token)
