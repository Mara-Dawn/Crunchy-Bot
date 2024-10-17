import asyncio
import contextlib
import copy
import datetime
from collections.abc import AsyncGenerator

import discord
from discord.ext import commands

from combat.actors import Actor
from combat.effects.effect import EmbedDataCollection
from combat.encounter import Encounter, EncounterContext
from combat.enemies.types import EnemyType
from config import Config
from control.combat.combat_embed_manager import CombatEmbedManager
from control.combat.object_factory import ObjectFactory
from control.controller import Controller
from control.logger import BotLogger
from control.service import Service
from control.settings_manager import SettingsManager
from datalayer.database import Database
from events.bot_event import BotEvent
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

            boss_type = {
                3: EnemyType.DADDY_P1,
                6: EnemyType.WEEB_BALL,
                # 9: None,
                # 12: None,
            }

            if guild_level in Config.BOSS_LEVELS:
                last_fight_event = await self.database.get_guild_last_boss_attempt(
                    guild_id, boss_type[guild_level]
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
                            with contextlib.suppress(discord.NotFound):
                                await message.delete()

                    if len(message.embeds) <= 0:
                        continue

                    embed_title = message.embeds[0].title
                    if embed_title[:16] == "Combat Zone":
                        await self.edit_message(message, embed=head_embed)

    async def delete_previous_combat_info(self, thread: discord.Thread | None):
        if thread is None:
            return
        async for message in thread.history(limit=100):
            if len(message.embeds) == 1 and message.author.id == self.bot.user.id:
                embed = message.embeds[0]
                if embed.image.url is not None and embed.title is not None:
                    view = discord.ui.View.from_message(message)
                    if view is not None:
                        self.controller.detach_view_by_id(view.id)
                    with contextlib.suppress(discord.NotFound):
                        await message.delete()
                    break

    async def delete_active_player_input(self, thread: discord.Thread | None):
        if thread is None:
            return
        async for message in thread.history(limit=100):
            if (  # noqa: SIM102
                len(message.embeds) > 0 and message.author.id == self.bot.user.id
            ):
                if len(message.content) > 0:
                    view = discord.ui.View.from_message(message)
                    if view is not None:
                        self.controller.detach_view_by_id(view.id)
                    with contextlib.suppress(discord.NotFound):
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

        if guild_level >= Config.MAX_LVL:
            await self.refresh_combat_messages(guild_id)
            return

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

                new_features = [
                    feature
                    for feature, level in Config.UNLOCK_LEVELS.items()
                    if level == guild_level
                ]

                if len(new_features) > 0:
                    announcement_list = []
                    for feature in new_features:
                        key_point = f"* {feature.value}"
                        announcement_list.append(key_point)
                    announcement += "\n\nUnlocked New Features:\n"
                    announcement += "\n".join(announcement_list)

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

    async def get_previous_round_message(
        self, thread: discord.Thread
    ) -> discord.Message:
        async for message in thread.history(limit=100):
            if len(message.embeds) >= 1 and message.author.id == self.bot.user.id:
                embed = message.embeds[0]
                if embed.title == "New Round" or embed.title == "Round Continued..":
                    return message
        return None

    async def refresh_round_overview(self, context: EncounterContext):
        round_message = await self.get_previous_round_message(context.thread)
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
        message = await self.get_previous_round_message(thread)

        if len(message.embeds) >= 10:
            round_embed = await self.embed_manager.get_round_embed(context, cont=True)
            message = await self.send_message(
                context.thread, content="", embed=round_embed
            )

        previous_embeds = message.embeds

        async for embed in generator:
            current_embeds = previous_embeds + [embed]
            await self.edit_message(message, embeds=current_embeds)

    async def update_current_turn_embed_by_generator(
        self,
        context: EncounterContext,
        generator: AsyncGenerator,
    ):
        thread = context.thread
        message = await self.get_previous_round_message(thread)
        base_embed = context.current_turn_embed

        embed_index = None
        if not context.current_actor.is_enemy:
            for index, message_embed in reversed(list(enumerate(message.embeds))):
                if (
                    message_embed.author is not None
                    and message_embed.author.name == base_embed.author.name
                ):
                    embed_index = index
                    break

        embeds = message.embeds

        previous_length = 0
        current_start = 0

        async for field_data in generator:
            embed = copy.deepcopy(base_embed)

            if embed_index is None:
                for field in field_data[current_start:]:
                    embed.add_field(
                        name=field.name, value=field.value, inline=field.inline
                    )
                base_embed = embed
                await self.append_embed_to_round(context, embed)
                message = await self.get_previous_round_message(thread)
                embed_index = len(message.embeds) - 1
                embeds = message.embeds
                previous_length = len(field_data)
                continue

            field_count = len(field_data) - current_start

            if field_count + len(embed.fields) > 25:
                new_embed = discord.Embed(color=embed.color)
                new_embed.set_thumbnail(url=embed.thumbnail.url)
                new_embed.set_author(name=embed.author.name)
                new_embed.set_thumbnail(url=embed.thumbnail.url)
                self.embed_manager.add_text_bar(new_embed, "", "Continued ...")
                base_embed = new_embed

                embed = copy.deepcopy(base_embed)
                await self.append_embed_to_round(context, embed)

                message = await self.get_previous_round_message(thread)
                embed_index = len(message.embeds) - 1
                embeds = message.embeds
                current_start = previous_length

            for field in field_data[current_start:]:
                embed.add_field(name=field.name, value=field.value, inline=field.inline)

            embeds[embed_index] = embed
            await self.edit_message(message, embeds=embeds)

            if previous_length == 0:
                base_embed = embed

            previous_length = len(field_data)

        context.current_turn_embed = embed

    async def update_current_turn_embed(
        self, context: EncounterContext, embed_data: EmbedDataCollection | None = None
    ):
        self.embed_manager.add_spacer_to_embed(context.current_turn_embed)
        thread = context.thread
        message = await self.get_previous_round_message(thread)

        embed_index = None

        if (
            embed_data is not None
            and len(context.current_turn_embed.fields) + embed_data.length > 25
        ):
            context.current_turn_embed = self.embed_manager.get_turn_embed(
                context.current_actor
            )
        else:
            for index, message_embed in reversed(list(enumerate(message.embeds))):
                if (
                    message_embed.author is not None
                    and message_embed.author.name
                    == context.current_turn_embed.author.name
                ):
                    embed_index = index
                    break

        if embed_data is not None:
            self.embed_manager.add_status_effect_to_embed(
                context.current_turn_embed, embed_data
            )

        if embed_index is None:
            return await self.append_embed_to_round(context, context.current_turn_embed)

        embeds = message.embeds
        embeds[embed_index] = context.current_turn_embed
        await self.edit_message(message, embeds=embeds)

    async def append_embed_to_round(
        self, context: EncounterContext, embed: discord.Embed
    ):
        thread = context.thread
        message = await self.get_previous_round_message(thread)

        if len(message.embeds) >= 10:
            round_embed = await self.embed_manager.get_round_embed(context, cont=True)
            message = await self.send_message(
                context.thread, content="", embed=round_embed
            )

        previous_embeds = message.embeds
        current_embeds = previous_embeds + [embed]
        await self.edit_message(message, embeds=current_embeds)

    async def append_embeds_to_round(
        self, context: EncounterContext, actor: Actor, embed_data: EmbedDataCollection
    ):
        message = None
        if embed_data.length <= 0:
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
