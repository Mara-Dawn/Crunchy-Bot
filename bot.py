from typing import Any, List
import discord
from discord.ext import commands
from datalayer.database import Database
from control.controller import Controller
from control.event_manager import EventManager
from control.item_manager import ItemManager
from control.logger import BotLogger
from control.role_manager import RoleManager
from control.settings import BotSettings


class CrunchyBot(commands.Bot):

    DB_FILE = "database.sqlite"
    LOG_FILE = "./log/marabot.log"
    TENOR_TOKEN_FILE = "tenor.txt"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.logger = BotLogger(self, self.LOG_FILE)
        self.database = Database(self, self.logger, self.DB_FILE)
        self.settings = BotSettings(self, self.database, self.logger)

        self.controller = Controller(self, self.logger, self.settings, self.database)

        self.role_manager = RoleManager(
            self, self.logger, self.settings, self.database, self.controller
        )
        self.event_manager = EventManager(
            self, self.logger, self.settings, self.database, self.controller
        )
        self.item_manager = ItemManager(
            self, self.logger, self.settings, self.database, self.controller
        )

    async def setup_hook(self) -> None:
        await self.load_extension("cogs.police")
        await self.load_extension("cogs.jail")
        await self.load_extension("cogs.interactions")
        await self.load_extension("cogs.statistics")
        await self.load_extension("cogs.quotes")
        await self.load_extension("cogs.beans.shop")
        await self.load_extension("cogs.beans.gamba")
        await self.load_extension("cogs.beans.beans")
        await self.load_extension("cogs.bully")

    async def on_guild_join(self, guild):
        self.logger.log(guild.id, "new guild registered.")

    async def on_guild_remove(self, guild):
        self.logger.log(guild.id, "guild removed.")

    async def command_response(
        self,
        module: str,
        interaction: discord.Interaction,
        message: str,
        args: List[Any] = None,
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
        args: List[Any] = None,
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
