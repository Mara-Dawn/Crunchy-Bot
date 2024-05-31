import datetime
import re
import typing

import discord
from bot import CrunchyBot
from control.ai_manager import AIManager
from control.controller import Controller
from control.event_manager import EventManager
from control.item_manager import ItemManager
from control.logger import BotLogger
from control.role_manager import RoleManager
from control.settings_manager import SettingsManager
from datalayer.database import Database
from datalayer.types import ItemTrigger
from discord import NotFound, Webhook, app_commands
from discord.ext import commands
from events.inventory_event import InventoryEvent
from items.types import ItemGroup, ItemType


class Bully(commands.Cog):

    def __init__(self, bot: CrunchyBot):
        self.bot = bot
        self.logger: BotLogger = bot.logger
        self.database: Database = bot.database
        self.controller: Controller = bot.controller
        self.item_manager: ItemManager = self.controller.get_service(ItemManager)
        self.event_manager: EventManager = self.controller.get_service(EventManager)
        self.role_manager: RoleManager = self.controller.get_service(RoleManager)
        self.ai_manager: AIManager = self.controller.get_service(AIManager)
        self.settings_manager: SettingsManager = self.controller.get_service(
            SettingsManager
        )
        self.webhooks: dict[int, Webhook] = {}

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

        if not await self.settings_manager.get_bully_enabled(guild_id):
            return

        if (
            message.channel.id
            in await self.settings_manager.get_bully_exclude_channels(guild_id)
        ):
            return

        user_items = await self.item_manager.get_guild_items_activated(
            guild_id, ItemTrigger.USER_MESSAGE
        )

        for user_id, items in user_items.items():
            for item in items:
                if item.type == ItemType.REACTION_SPAM:
                    target_id, emoji = await self.database.get_bully_react(
                        guild_id, user_id
                    )

                    if message.author.id != target_id:
                        continue

                    if emoji is None:
                        continue
                    try:
                        current_message = await message.channel.fetch_message(
                            message.id
                        )
                    except NotFound:
                        continue

                    if emoji in [x.emoji for x in current_message.reactions]:
                        continue

                    await message.add_reaction(emoji)

                    event = InventoryEvent(
                        datetime.datetime.now(),
                        guild_id,
                        user_id,
                        item.type,
                        -1,
                    )
                    await self.controller.dispatch_event(event)
                if item.group == ItemGroup.DEBUFF:
                    if message.author.id != user_id:
                        continue
                    if (
                        message.channel.id
                        not in await self.settings_manager.get_beans_channels(guild_id)
                        and message.channel.id
                        not in await self.settings_manager.get_jail_channels(guild_id)
                    ):
                        continue
                    await self.modify_message(item.type, message)
                    return

    async def modify_message(self, item_type: ItemType, message: discord.Message):
        content = message.content
        original_message = content
        channel = message.channel
        author = message.author
        guild_id = message.guild.id
        attachments = message.attachments

        if channel.type == "public_thread" or channel.type == "private_thread":
            return

        if len(content) <= 0:
            return

        if len(re.sub(r"<a?:\w*:\d*>", "", content)) == 0:
            return

        filtered_message = ""
        start = 0
        for match in re.finditer(r"<a?:\w*:\d*>", content):
            end, newstart = match.span()
            filtered_message += content[start:end]
            emoji = match.group()
            emoji_id = emoji.split("<")[1].split(":")[-1].rstrip(">")
            if self.bot.get_emoji(int(emoji_id)) is not None:
                filtered_message += emoji
            start = newstart
        filtered_message += content[start:]
        content = " ".join(filtered_message.split())

        await message.delete()

        generated_content = ""

        match item_type:
            case ItemType.HIGH_AS_FRICK:
                generated_content = await self.ai_manager.stonerfy(content)
            case ItemType.EGIRL_DEBUFF:
                generated_content = await self.ai_manager.uwufy(content)
            case ItemType.RELIGION_DEBUFF:
                generated_content = await self.ai_manager.religify(content)
            case ItemType.ALCOHOL_DEBUFF:
                generated_content = await self.ai_manager.alcoholify(content)
            case ItemType.WEEB_DEBUFF:
                generated_content = await self.ai_manager.weebify(content)
            case ItemType.BRIT_DEBUFF:
                generated_content = await self.ai_manager.britify(content)
            case ItemType.MEOW_DEBUFF:
                generated_content = await self.ai_manager.meowify(content)
            case ItemType.NERD_DEBUFF:
                generated_content = await self.ai_manager.nerdify(content)
            case ItemType.TRUMP_DEBUFF:
                generated_content = await self.ai_manager.trumpify(content)

        generated_content = (
            generated_content + f"\n||original message: {original_message}||"
        )

        if channel.id not in self.webhooks:
            webhooks = await message.channel.webhooks()
            if webhooks is not None:
                if len(webhooks) > 1:
                    for webhook in webhooks:
                        await webhook.delete()
                elif len(webhooks) == 1:
                    self.webhooks[channel.id] = webhooks[0]
            if channel.id not in self.webhooks:
                self.webhooks[channel.id] = await channel.create_webhook(
                    name="Possession"
                )

        files = [await attachment.to_file() for attachment in attachments]

        await self.webhooks[channel.id].send(
            content=generated_content,
            username=author.display_name,
            avatar_url=author.display_avatar,
            files=files,
        )

        if len(generated_content) <= 0:
            return

        event = InventoryEvent(
            datetime.datetime.now(),
            guild_id,
            author.id,
            item_type,
            -1,
        )
        await self.controller.dispatch_event(event)

    group = app_commands.Group(
        name="bully", description="Subcommands for the Bully module."
    )

    @group.command(
        name="settings",
        description="Overview of all bully related settings and their current value.",
    )
    @app_commands.check(__has_permission)
    async def get_settings(self, interaction: discord.Interaction):
        output = await self.settings_manager.get_settings_string(
            interaction.guild_id, SettingsManager.BULLY_SUBSETTINGS_KEY
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
        await self.settings_manager.set_bully_enabled(
            interaction.guild_id, enabled == "on"
        )
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
        await self.settings_manager.add_bully_exclude_channel(
            interaction.guild_id, channel.id
        )
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
        await self.settings_manager.remove_bully_exclude_channel(
            interaction.guild_id, channel.id
        )
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"Resuming bullying in {channel.name}.",
            args=[channel],
        )

    # @group.command(
    #     name="disable_haunts", description="Stop haunting in specific channels."
    # )
    # @app_commands.describe(channel="Stop haunting for this channel.")
    # @app_commands.check(__has_permission)
    # async def disable_haunts(
    #     self, interaction: discord.Interaction, channel: discord.TextChannel
    # ):
    #     await interaction.response.defer(ephemeral=True)
    #     await self.settings_manager.add_haunt_exclude_channel(
    #         interaction.guild_id, channel.id
    #     )
    #     await self.bot.command_response(
    #         self.__cog_name__,
    #         interaction,
    #         f"Stopping haunting in {channel.name}.",
    #         args=[channel],
    #     )

    # @group.command(
    #     name="reenable_haunts", description="Reenable haunting for specific channels."
    # )
    # @app_commands.describe(channel="Reenable haunting for this channel.")
    # @app_commands.check(__has_permission)
    # async def reenable_haunts(
    #     self, interaction: discord.Interaction, channel: discord.TextChannel
    # ):
    #     await interaction.response.defer(ephemeral=True)
    #     await self.settings_manager.remove_haunt_exclude_channel(
    #         interaction.guild_id, channel.id
    #     )
    #     await self.bot.command_response(
    #         self.__cog_name__,
    #         interaction,
    #         f"Resuming haunting in {channel.name}.",
    #         args=[channel],
    #     )


async def setup(bot):
    await bot.add_cog(Bully(bot))
