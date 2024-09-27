import sys
from typing import Any

import discord
from discord.ext import commands

from control.controller import Controller
from control.logger import BotLogger
from datalayer.database import Database
from error import ErrorHandler


class CrunchyBot(commands.Bot):

    LOG_FILE = "./log/marabot.log"
    DB_FILE = "database.sqlite"
    ADMIN_ID = "ADMIN_USER_ID"
    SYNC_PERMISSIONS = "ADDITIONAL_SYNC_PERMISSIONS"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    async def setup_hook(self) -> None:
        self.logger = BotLogger(self, self.LOG_FILE)
        self.database = Database(self, self.logger, self.DB_FILE)
        self.controller = Controller(self, self.logger, self.database)

        await self.database.create_tables()

        await self.load_extension("cogs.police")
        await self.load_extension("cogs.jail")
        await self.load_extension("cogs.interactions")
        await self.load_extension("cogs.statistics")
        await self.load_extension("cogs.quotes")
        await self.load_extension("cogs.beans.shop")
        await self.load_extension("cogs.beans.gamba")
        await self.load_extension("cogs.beans.beans")
        await self.load_extension("cogs.bully")
        await self.load_extension("cogs.chat")
        await self.load_extension("cogs.combat")

    async def on_guild_join(self, guild):
        self.logger.log(guild.id, "new guild registered.")

    async def on_guild_remove(self, guild):
        self.logger.log(guild.id, "guild removed.")

    async def command_response(
        self,
        module: str,
        interaction: discord.Interaction,
        message: str,
        embeds: list[discord.Embed] | None = None,
        args: list[Any] = None,
        ephemeral: bool = True,
    ) -> None:
        if args is None:
            args = []
        return await self.response(
            module,
            interaction,
            message,
            interaction.command.name,
            embeds,
            args,
            ephemeral,
        )

    async def response(
        self,
        module: str,
        interaction: discord.Interaction,
        message: str,
        command: str,
        embeds: list[discord.Embed] | None = None,
        args: list[Any] = None,
        ephemeral: bool = True,
    ) -> None:
        if args is None:
            args = []
        if embeds is None:
            embeds = []
        log_message = f"{interaction.user.name} used command `{command}`."

        if len(args) > 0:
            log_message += " Arguments: " + ", ".join([str(x) for x in args])

        self.logger.log(interaction.guild_id, log_message, cog=module)
        allowed_mentions = discord.AllowedMentions(roles=True)
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    message,
                    ephemeral=ephemeral,
                    embeds=embeds,
                    allowed_mentions=allowed_mentions,
                )
            else:
                await interaction.followup.send(
                    message,
                    ephemeral=ephemeral,
                    embeds=embeds,
                    allowed_mentions=allowed_mentions,
                )
        except discord.errors.InteractionResponded:
            await interaction.followup.send(
                message,
                ephemeral=ephemeral,
                embeds=embeds,
                allowed_mentions=allowed_mentions,
            )
