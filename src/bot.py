from typing import Any

import discord
from control.controller import Controller
from control.logger import BotLogger
from datalayer.database import Database
from discord.ext import commands


class CrunchyBot(commands.Bot):

    LOG_FILE = "./log/marabot.log"
    TENOR_TOKEN_FILE = "tenor.txt"
    SEASON_DB_FILE = "season.sqlite"
    CORE_DB_FILE = "database.sqlite"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    async def setup_hook(self) -> None:
        self.logger = BotLogger(self, self.LOG_FILE)
        self.database = Database(
            self, self.logger, self.CORE_DB_FILE, self.SEASON_DB_FILE
        )
        self.controller = Controller(self, self.logger, self.database)

        await self.database.init()

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

    async def on_guild_join(self, guild):
        self.logger.log(guild.id, "new guild registered.")

    async def on_guild_remove(self, guild):
        self.logger.log(guild.id, "guild removed.")

    async def command_response(
        self,
        module: str,
        interaction: discord.Interaction,
        message: str,
        args: list[Any] = None,
        ephemeral: bool = True,
    ) -> None:
        if args is None:
            args = []
        return await self.response(
            module, interaction, message, interaction.command.name, args, ephemeral
        )

    async def response(
        self,
        module: str,
        interaction: discord.Interaction,
        message: str,
        command: str,
        args: list[Any] = None,
        ephemeral: bool = True,
    ) -> None:
        if args is None:
            args = []
        log_message = f"{interaction.user.name} used command `{command}`."

        if len(args) > 0:
            log_message += " Arguments: " + ", ".join([str(x) for x in args])

        self.logger.log(interaction.guild_id, log_message, cog=module)
        allowed_mentions = discord.AllowedMentions(roles=True)
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    message, ephemeral=ephemeral, allowed_mentions=allowed_mentions
                )
            else:
                await interaction.followup.send(
                    message, ephemeral=ephemeral, allowed_mentions=allowed_mentions
                )
        except discord.errors.InteractionResponded:
            await interaction.followup.send(
                message, ephemeral=ephemeral, allowed_mentions=allowed_mentions
            )
