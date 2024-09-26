import traceback
import io

import discord
from discord import app_commands
from discord.ext import commands

from control.logger import BotLogger


class ErrorHandler:

    def __init__(self, bot: commands.Bot) -> None:
        self.channel_id = 1288910317866319994
        self.bot = bot

    async def on_tree_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
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

            await self.post_error(error, interaction)
            raise error

    async def post_error(
        self, error: Exception, interaction: discord.Interaction | None = None
    ):
        channel = self.bot.get_channel(self.channel_id)
        webhooks = await channel.webhooks()
        if webhooks is not None and len(webhooks) > 0:
            webhook = webhooks[0]
        else:
            webhook = await channel.create_webhook(name="Error")

        content = f"<@{90043934247501824}>\n\n"
        if interaction is not None:
            content += f"Guild: **{interaction.guild.name}** ({interaction.guild.id})\n"
            content += (
                f"User: **{interaction.user.display_name}** ({interaction.user.id})\n"
            )
        trace = "".join(traceback.format_exception(error))
        textfile = io.StringIO(trace)
        file = discord.File(textfile, "trace.txt")
        # content += f"```{trace}\n```"

        content += "\n**Previous Log**:\n"
        logger: BotLogger = self.bot.logger
        cache = logger.cache
        content += f"```{"\n".join(cache)}```"

        await webhook.send(
            content=content,
            username=self.bot.user.display_name,
            avatar_url=self.bot.user.display_avatar,
            files=[file],
        )
