import asyncio
import datetime
from collections.abc import AsyncGenerator

import discord
from discord.ext import commands

from combat.actors import Actor
from combat.encounter import Encounter, EncounterContext
from config import Config
from control.combat.combat_embed_manager import CombatEmbedManager
from control.combat.context_loader import ContextLoader
from control.combat.object_factory import ObjectFactory
from control.controller import Controller
from control.logger import BotLogger
from control.service import Service
from control.settings_manager import SettingsManager
from datalayer.database import Database
from events.bot_event import BotEvent
from events.types import EncounterEventType, EventType
from view.combat.embed import EnemyOverviewEmbed


class DiscordManager(Service):

    RETRY_LIMIT = 5

    def __init__(
        self,
        bot: commands.Bot,
        logger: BotLogger,
        database: Database,
        controller: Controller,
    ):
        super().__init__(bot, logger, database)
        self.controller = controller
        self.settings_manager: SettingsManager = self.controller.get_service(
            SettingsManager
        )
        self.embed_manager: CombatEmbedManager = self.controller.get_service(
            CombatEmbedManager
        )
        self.factory: ObjectFactory = self.controller.get_service(ObjectFactory)
        self.context_loader: ContextLoader = self.controller.get_service(ContextLoader)
        self.log_name = "Discord"

    async def listen_for_event(self, event: BotEvent):
        pass

    async def create_encounter_thread(self, encounter: Encounter) -> discord.Thread:
        channel = self.bot.get_channel(encounter.channel_id)
        enemy = await self.factory.get_enemy(encounter.enemy_type)
        thread = await channel.create_thread(
            name=f"Encounter: {enemy.name}",
            type=discord.ChannelType.public_thread,
            auto_archive_duration=60,
        )

        await self.database.log_encounter_thread(
            encounter.id, thread.id, encounter.guild_id, encounter.channel_id
        )

        return thread

    async def refresh_combat_messages(self, guild_id: int, purge: bool = False):
        combat_channels = await self.settings_manager.get_combat_channels(guild_id)

        guild = self.bot.get_guild(guild_id)

        for channel_id in combat_channels:
            channel = guild.get_channel(channel_id)
            if channel is None:
                continue

            guild_level = await self.database.get_guild_level(guild.id)

            progress, requirement = await self.database.get_guild_level_progress(
                guild.id, guild_level
            )

            start_hour = await self.settings_manager.get_combat_max_lvl_start(guild.id)
            end_hour = await self.settings_manager.get_combat_max_lvl_end(guild.id)

            current_time = datetime.datetime.now()
            current_hour = current_time.hour

            post_start = start_hour <= current_hour
            pre_end = current_hour < end_hour
            enemies_asleep = False
            wakeup = current_time

            if start_hour < end_hour:
                if current_time.weekday() in [4, 5] and not pre_end:
                    pre_end = True
                if current_time.weekday() in [5, 6] and not post_start:
                    post_start = True
                if not (post_start and pre_end):
                    enemies_asleep = True
            else:
                if current_time.weekday() in [5, 6] and not pre_end:
                    pre_end = True
                if current_time.weekday() in [5, 6] and not post_start:
                    post_start = True
                if not (post_start or pre_end):
                    enemies_asleep = True

            additional_info = None
            if enemies_asleep:
                if current_hour > start_hour:
                    wakeup = current_time + datetime.timedelta(days=1)
                wakeup = wakeup.replace(hour=start_hour, minute=0)
                additional_info = f"**\nThe enemies of level {guild_level} and above are currently asleep.\n"
                additional_info += (
                    f"They will return <t:{int(wakeup.timestamp())}:R> **"
                )

            fresh_prog = True
            if guild_level in Config.BOSS_LEVELS:
                last_fight_event = await self.database.get_guild_last_boss_attempt(
                    guild_id, Config.BOSS_TYPE[guild_level]
                )
                fresh_prog = last_fight_event is None

            head_embed = EnemyOverviewEmbed(
                self.bot.user,
                guild_level,
                requirement,
                progress,
                fresh_prog,
                additional_info,
            )

            if purge:
                await channel.purge()
                await self.send_message(channel, content="", embed=head_embed)
            else:
                async for message in channel.history(limit=100):
                    if message.thread is not None:
                        age_delta = (
                            datetime.datetime.now(datetime.UTC) - message.created_at
                        )
                        if age_delta.total_seconds() > 60 * 60:
                            await message.delete()

                    if len(message.embeds) <= 0:
                        continue

                    embed_title = message.embeds[0].title
                    if embed_title[:16] == "Combat Zone":
                        await self.edit_message(message, embed=head_embed)

    async def delete_previous_combat_info(self, thread: discord.Thread):
        async for message in thread.history(limit=100):
            if len(message.embeds) == 1 and message.author.id == self.bot.user.id:
                embed = message.embeds[0]
                if embed.image.url is not None and embed.title is not None:
                    view = discord.ui.View.from_message(message)
                    if view is not None:
                        self.controller.detach_view_by_id(view.id)
                    await message.delete()
                    break

    async def get_previous_enemy_info(self, thread: discord.Thread):
        async for message in thread.history(limit=100):
            if len(message.embeds) == 1 and message.author.id == self.bot.user.id:
                embed = message.embeds[0]
                if embed.image.url is not None and embed.title is not None:
                    return message
        return None

    async def update_guild_status(self, guild_id: int):
        combat_channels = await self.settings_manager.get_combat_channels(guild_id)
        guild = self.bot.get_guild(guild_id)

        guild_level = await self.database.get_guild_level(guild.id)

        progress, requirement = await self.database.get_guild_level_progress(
            guild.id, guild_level
        )

        if progress >= requirement and (guild_level) not in Config.BOSS_LEVELS:
            guild_level += 1
            await self.database.set_guild_level(guild.id, guild_level)

            bean_channels = await self.settings_manager.get_beans_notification_channels(
                guild_id
            )
            beans_role_id = await self.settings_manager.get_beans_role(guild_id)
            guild = self.bot.get_guild(guild_id)
            if guild is not None:
                announcement = (
                    "**A new Level has been unlocked!**\n"
                    f"Congratulations! You fulfilled the requirements to reach **Level {guild_level}**.\n"
                    "Good luck facing the challenges ahead, stronger opponents and greater rewards are waiting for you."
                )
                if beans_role_id is not None:
                    announcement += f"\n<@&{beans_role_id}>"

                for channel_id in bean_channels:
                    channel = guild.get_channel(channel_id)
                    if channel is not None:
                        await channel.send(announcement)

        for channel_id in combat_channels:
            channel = guild.get_channel(channel_id)
            if channel is None:
                continue

            await self.refresh_combat_messages(guild_id)

    async def get_previous_turn_message(self, thread: discord.Thread):
        async for message in thread.history(limit=100):
            if len(message.embeds) >= 1 and message.author.id == self.bot.user.id:
                embed = message.embeds[0]
                if embed.title == "New Round" or embed.title == "Round Continued..":
                    return message
        return None

    async def refresh_round_overview(self, context: EncounterContext):
        round_message = await self.get_previous_turn_message(context.thread)
        if round_message is not None:
            round_embeds = round_message.embeds
            cont = round_embeds[0].title == "Round Continued.."
            round_embed = await self.embed_manager.get_round_embed(context, cont=cont)
            round_embeds[0] = round_embed
            await self.edit_message(round_message, embeds=round_embeds, attachments=[])

    async def append_embed_generator_to_round(
        self, context: EncounterContext, generator: AsyncGenerator
    ):
        thread = context.thread
        message = await self.get_previous_turn_message(thread)

        if len(message.embeds) >= 10:
            round_embed = await self.embed_manager.get_round_embed(context, cont=True)
            message = await self.send_message(
                context.thread, content="", embed=round_embed
            )

        previous_embeds = message.embeds

        async for embed in generator:
            current_embeds = previous_embeds + [embed]
            await self.edit_message(message, embeds=current_embeds)

    async def append_embed_to_round(
        self, context: EncounterContext, embed: discord.Embed
    ):
        thread = context.thread
        message = await self.get_previous_turn_message(thread)

        if len(message.embeds) >= 10:
            round_embed = await self.embed_manager.get_round_embed(context, cont=True)
            message = await self.send_message(
                context.thread, content="", embed=round_embed
            )

        previous_embeds = message.embeds
        current_embeds = previous_embeds + [embed]
        await self.edit_message(message, embeds=current_embeds)

    async def append_embeds_to_round(
        self, context: EncounterContext, actor: Actor, embed_data: dict[str, str]
    ):
        message = None
        if len(embed_data) <= 0:
            return message
        status_effect_embed = self.embed_manager.get_status_effect_embed(
            actor, embed_data
        )
        message = await self.append_embed_to_round(context, status_effect_embed)
        return message

    async def edit_message(self, message: discord.Message, **kwargs):
        retries = 0
        success = False
        new_message = None
        while not success and retries <= self.RETRY_LIMIT:
            try:
                new_message = await message.edit(**kwargs)
                success = True
            except (discord.HTTPException, discord.DiscordServerError) as e:
                self.logger.log(message.guild.id, e.text, self.log_name)
                retries += 1
                await asyncio.sleep(5)

        if not success:
            self.logger.error(message.guild.id, "edit message timeout", self.log_name)

        return new_message

    async def send_message(self, channel: discord.channel.TextChannel, **kwargs):
        retries = 0
        success = False
        message = None
        while not success and retries <= self.RETRY_LIMIT:
            try:
                message = await channel.send(**kwargs)
                success = True
            except (discord.HTTPException, discord.DiscordServerError) as e:
                self.logger.log(channel.guild.id, e.text, self.log_name)
                retries += 1
                await asyncio.sleep(5)

        if not success:
            self.logger.error(message.guild.id, "send message timeout", self.log_name)

        return message
