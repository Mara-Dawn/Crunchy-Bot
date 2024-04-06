import datetime
import typing
import discord
from discord import app_commands
from discord.ext import commands
from bot import CrunchyBot
from datalayer.database import Database
from datalayer.types import ItemTrigger
from control.controller import Controller
from control.event_manager import EventManager
from control.item_manager import ItemManager
from control.logger import BotLogger
from control.role_manager import RoleManager
from control.settings import BotSettings
from items.types import ItemType
from events.inventory_event import InventoryEvent


class Bully(commands.Cog):

    def __init__(self, bot: CrunchyBot):
        self.bot = bot
        self.logger: BotLogger = bot.logger
        self.settings: BotSettings = bot.settings
        self.database: Database = bot.database
        self.role_manager: RoleManager = bot.role_manager
        self.event_manager: EventManager = bot.event_manager
        self.item_manager: ItemManager = bot.item_manager
        self.controller: Controller = bot.controller

    @staticmethod
    async def __has_permission(interaction: discord.Interaction) -> bool:
        author_id = 90043934247501824
        return (
            interaction.user.id == author_id
            or interaction.user.guild_permissions.administrator
        )

    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.log(
            "init", str(self.__cog_name__) + " loaded.", cog=self.__cog_name__
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id == self.bot.user.id:
            return

        if message.author.bot:
            return

        if not message.guild:
            return

        guild_id = message.guild.id

        if not self.settings.get_bully_enabled(guild_id):
            return

        if message.channel.id in self.settings.get_bully_exclude_channels(guild_id):
            return

        user_items = await self.item_manager.get_guild_items_activated(
            guild_id, ItemTrigger.USER_MESSAGE
        )

        for user_id, items in user_items.items():
            for item in items:
                match item.get_type():
                    case ItemType.REACTION_SPAM:

                        target_id, emoji = self.database.get_bully_react(
                            guild_id, user_id
                        )

                        if message.author.id != target_id:
                            continue

                        if emoji is None:
                            continue

                        current_message = await message.channel.fetch_message(
                            message.id
                        )
                        if emoji in [x.emoji for x in current_message.reactions]:
                            continue

                        await message.add_reaction(emoji)

                        event = InventoryEvent(
                            datetime.datetime.now(),
                            guild_id,
                            user_id,
                            item.get_type(),
                            -1,
                        )
                        await self.controller.dispatch_event(event)

                    case _:
                        continue

    group = app_commands.Group(
        name="bully", description="Subcommands for the Bully module."
    )

    @group.command(
        name="settings",
        description="Overview of all bully related settings and their current value.",
    )
    @app_commands.check(__has_permission)
    async def get_settings(self, interaction: discord.Interaction):
        output = self.settings.get_settings_string(
            interaction.guild_id, BotSettings.BULLY_SUBSETTINGS_KEY
        )
        await self.bot.command_response(self.__cog_name__, interaction, output)

    @group.command(
        name="toggle", description="Enable or disable the entire Bully module."
    )
    @app_commands.describe(enabled="Turns the Bully module on or off.")
    @app_commands.check(__has_permission)
    async def set_toggle(
        self, interaction: discord.Interaction, enabled: typing.Literal["on", "off"]
    ):
        self.settings.set_bully_enabled(interaction.guild_id, enabled == "on")
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"Bully module was turned {enabled}.",
            args=[enabled],
        )

    @group.command(
        name="untrack_channel", description="Stop bullying in specific channels."
    )
    @app_commands.describe(channel="Stop bullying for this channel.")
    @app_commands.check(__has_permission)
    async def untrack_channel(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ):
        await interaction.response.defer(ephemeral=True)
        self.settings.add_bully_exclude_channel(interaction.guild_id, channel.id)
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"Stopping bullying in {channel.name}.",
            args=[channel],
        )

    @group.command(
        name="track_channel", description="Reenable bullying for specific channels."
    )
    @app_commands.describe(channel="Reenable bullying for this channel.")
    @app_commands.check(__has_permission)
    async def track_channel(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ):
        await interaction.response.defer(ephemeral=True)
        self.settings.remove_bully_exclude_channel(interaction.guild_id, channel.id)
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"Resuming bullying in {channel.name}.",
            args=[channel],
        )


async def setup(bot):
    await bot.add_cog(Bully(bot))
