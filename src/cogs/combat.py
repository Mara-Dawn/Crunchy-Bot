import datetime
import os
import random
import traceback
from collections import Counter
from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands, tasks

from bot import CrunchyBot
from combat.enchantments.types import EnchantmentType
from combat.enemies.enemy import Enemy
from combat.enemies.types import EnemyType
from combat.gear.types import GearBaseType, Rarity
from combat.skills.skill import Skill
from combat.skills.types import SkillEffect, SkillType
from control.combat.combat_actor_manager import CombatActorManager
from control.combat.combat_embed_manager import CombatEmbedManager
from control.combat.combat_gear_manager import CombatGearManager
from control.combat.discord_manager import DiscordManager
from control.combat.encounter_manager import EncounterManager
from control.combat.object_factory import ObjectFactory
from control.controller import Controller
from control.imgur_manager import ImgurManager
from control.logger import BotLogger
from control.settings_manager import SettingsManager
from control.types import UserSettingType
from control.user_settings_manager import UserSettingsManager
from datalayer.database import Database
from error import ErrorHandler
from events.encounter_event import EncounterEvent
from events.types import EncounterEventType, UIEventType
from events.ui_event import UIEvent
from items.types import ItemType
from view.combat.embed import EquipmentHeadEmbed
from view.combat.gear_menu_view import GearMenuView
from view.settings_modal import SettingsModal


class Combat(commands.Cog):

    ENCOUNTER_MIN_WAIT = 40
    ENCOUNTER_MAX_WAIT = 60

    LOW_LVL_ENCOUNTER_MIN_WAIT = 20
    LOW_LVL_ENCOUNTER_MAX_WAIT = 30

    def __init__(self, bot: CrunchyBot) -> None:
        self.bot = bot
        self.logger: BotLogger = bot.logger
        self.database: Database = bot.database
        self.controller: Controller = bot.controller
        self.encounter_manager: EncounterManager = self.controller.get_service(
            EncounterManager
        )
        self.settings_manager: SettingsManager = self.controller.get_service(
            SettingsManager
        )
        self.user_settings_manager: UserSettingsManager = self.controller.get_service(
            UserSettingsManager
        )
        self.gear_manager: CombatGearManager = self.controller.get_service(
            CombatGearManager
        )
        self.embed_manager: CombatEmbedManager = self.controller.get_service(
            CombatEmbedManager
        )
        self.actor_manager: CombatActorManager = self.controller.get_service(
            CombatActorManager
        )
        self.discord: DiscordManager = self.controller.get_service(DiscordManager)
        self.imgur_manager: ImgurManager = self.controller.get_service(ImgurManager)
        self.factory: ObjectFactory = self.controller.get_service(ObjectFactory)
        self.enemy_timers = {}
        self.enemy_timers_low_lvl = {}

    @staticmethod
    async def __has_permission(interaction: discord.Interaction) -> bool:
        author_id = int(os.environ.get(CrunchyBot.ADMIN_ID))
        return (
            interaction.user.id == author_id
            or interaction.user.guild_permissions.administrator
        )

    async def __check_enabled(
        self, interaction: discord.Interaction, all_channels: bool = False
    ):
        guild_id = interaction.guild_id

        if not await self.settings_manager.get_combat_enabled(guild_id):
            await self.bot.command_response(
                self.__cog_name__,
                interaction,
                "Combat module is currently disabled.",
            )
            return False

        if (
            not all_channels
            and interaction.channel_id
            not in await self.settings_manager.get_beans_channels(guild_id)
        ):
            await self.bot.command_response(
                self.__cog_name__,
                interaction,
                "Combat related commands cannot be used in this channel.",
            )
            return False

        return True

    async def __beans_role_check(self, interaction: discord.Interaction) -> bool:
        member = interaction.user
        guild_id = interaction.guild_id

        beans_role = await self.settings_manager.get_beans_role(guild_id)
        if beans_role is None:
            return True
        if beans_role in [role.id for role in member.roles]:
            return True

        role_name = interaction.guild.get_role(beans_role).name
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"You can only use this command if you have the role `{role_name}`.",
        )
        return False

    async def __reevaluate_next_enemy(self, guild_id: int) -> None:
        next_spawn_delay = random.randint(
            self.ENCOUNTER_MIN_WAIT, self.ENCOUNTER_MAX_WAIT
        )
        self.logger.log(
            guild_id,
            f"New random enemy interval: {next_spawn_delay} minutes.",
            cog=self.__cog_name__,
        )
        next_spawn = datetime.datetime.now() + datetime.timedelta(
            minutes=next_spawn_delay
        )
        self.enemy_timers[guild_id] = next_spawn

    async def __reevaluate_next_low_lvl_enemy(self, guild_id: int) -> None:
        next_spawn_delay = random.randint(
            self.LOW_LVL_ENCOUNTER_MIN_WAIT, self.LOW_LVL_ENCOUNTER_MAX_WAIT
        )
        self.logger.log(
            guild_id,
            f"New random low lvl enemy interval: {next_spawn_delay} minutes.",
            cog=self.__cog_name__,
        )
        next_spawn = datetime.datetime.now() + datetime.timedelta(
            minutes=next_spawn_delay
        )
        self.enemy_timers_low_lvl[guild_id] = next_spawn

    @commands.Cog.listener("on_ready")
    async def on_ready_combat(self):
        for guild in self.bot.guilds:
            await self.discord.refresh_combat_messages(guild.id, purge=True)
        self.random_encounter_task.start()
        self.random_low_lvl_encounter_task.start()
        self.logger.log("init", "Combat loaded.", cog=self.__cog_name__)

    @commands.Cog.listener("on_guild_join")
    async def on_guild_join_combat(self, guild):
        self.logger.log(
            guild.id, "Adding enemy timer for new guild.", cog=self.__cog_name__
        )
        await self.__reevaluate_next_enemy(guild.id)
        await self.__reevaluate_next_low_lvl_enemy(guild.id)

    @commands.Cog.listener("on_guild_remove")
    async def on_guild_remove_combat(self, guild):
        del self.enemy_timers[guild.id]
        del self.enemy_timers_low_lvl[guild.id]

    @tasks.loop(minutes=1)
    async def random_encounter_task(self):
        self.logger.debug(
            "sys", "Random Encounter task started.", cog=self.__cog_name__
        )

        try:
            for guild in self.bot.guilds:
                if guild.id not in self.enemy_timers:
                    continue

                if not await self.settings_manager.get_combat_enabled(guild.id):
                    continue

                current_time = datetime.datetime.now()
                if current_time < self.enemy_timers[guild.id]:
                    continue

                start_hour = await self.settings_manager.get_combat_max_lvl_start(
                    guild.id
                )
                end_hour = await self.settings_manager.get_combat_max_lvl_end(guild.id)

                current_hour = current_time.hour

                post_start = start_hour <= current_hour
                pre_end = current_hour < end_hour

                if start_hour < end_hour:
                    if current_time.weekday() in [4, 5] and not pre_end:
                        pre_end = True
                    if current_time.weekday() in [5, 6] and not post_start:
                        post_start = True
                    if not (post_start and pre_end):
                        continue
                else:
                    if current_time.weekday() in [5, 6] and not pre_end:
                        pre_end = True
                    if current_time.weekday() in [5, 6] and not post_start:
                        post_start = True
                    if not (post_start or pre_end):
                        continue

                self.logger.log("sys", "Enemy timeout reached.", cog=self.__cog_name__)
                await self.__reevaluate_next_enemy(guild.id)

                combat_channels = await self.settings_manager.get_combat_channels(
                    guild.id
                )
                if len(combat_channels) == 0:
                    continue

                encounter_level = await self.database.get_guild_level(guild.id)

                await self.encounter_manager.spawn_encounter(
                    guild, level=encounter_level
                )
        except Exception as e:
            print(traceback.format_exc())
            error_handler = ErrorHandler(self.bot)
            await error_handler.post_error(e)

    @tasks.loop(minutes=1)
    async def random_low_lvl_encounter_task(self):
        self.logger.debug(
            "sys", "Random low lvl Encounter task started.", cog=self.__cog_name__
        )

        try:
            for guild in self.bot.guilds:
                if guild.id not in self.enemy_timers_low_lvl:
                    continue

                max_encounter_level = await self.database.get_guild_level(guild.id) - 1
                max_encounter_level = max(1, max_encounter_level)

                if max_encounter_level <= 0:
                    continue

                if datetime.datetime.now() < self.enemy_timers_low_lvl[guild.id]:
                    continue

                if not await self.settings_manager.get_combat_enabled(guild.id):
                    continue

                self.logger.log(
                    "sys", "Low Lvl Enemy timeout reached.", cog=self.__cog_name__
                )
                await self.__reevaluate_next_low_lvl_enemy(guild.id)

                combat_channels = await self.settings_manager.get_combat_channels(
                    guild.id
                )
                if len(combat_channels) == 0:
                    continue

                encounter_level = random.randint(1, max_encounter_level)

                await self.encounter_manager.spawn_encounter(
                    guild, level=encounter_level
                )
        except Exception as e:
            print(traceback.format_exc())
            error_handler = ErrorHandler(self.bot)
            await error_handler.post_error(e)

    @random_encounter_task.before_loop
    async def random_encounter_task_before(self):
        try:
            self.logger.log(
                "sys", "Random Encounter before loop started.", cog=self.__cog_name__
            )
            for guild in self.bot.guilds:
                if not await self.settings_manager.get_combat_enabled(guild.id):
                    continue

                if len(await self.settings_manager.get_combat_channels(guild.id)) <= 0:
                    continue

                max_encounter_level = await self.database.get_guild_level(guild.id)
                encounter_event = await self.database.get_last_encounter_spawn_event(
                    guild.id, min_lvl=max_encounter_level
                )
                last_spawn = datetime.datetime.now()

                if encounter_event is None:
                    self.logger.log(
                        guild.id,
                        "No previous spawns, next spawn imminent.",
                        cog=self.__cog_name__,
                    )
                    self.enemy_timers[guild.id] = last_spawn
                    continue

                if encounter_event is not None:
                    last_spawn = encounter_event.datetime

                diff = datetime.datetime.now() - last_spawn
                diff_minutes = int(diff.total_seconds() / 60)
                self.logger.log(
                    guild.id,
                    f"Last spawn was {diff_minutes} minutes ago.",
                    cog=self.__cog_name__,
                )

                min_wait = self.ENCOUNTER_MIN_WAIT
                if diff_minutes < self.ENCOUNTER_MAX_WAIT:
                    min_wait = max(self.ENCOUNTER_MIN_WAIT, diff_minutes)

                next_drop_delay = random.randint(min_wait, self.ENCOUNTER_MAX_WAIT)
                self.logger.log(
                    guild.id,
                    f"Random spawn delay: {next_drop_delay} minutes.",
                    cog=self.__cog_name__,
                )
                next_spawn = last_spawn + datetime.timedelta(minutes=next_drop_delay)
                diff = next_spawn - datetime.datetime.now()
                self.logger.log(
                    guild.id,
                    f"Next spawn in {int(diff.total_seconds()/60)} minutes.",
                    cog=self.__cog_name__,
                )

                self.enemy_timers[guild.id] = next_spawn
        except Exception as e:
            print(traceback.format_exc())
            error_handler = ErrorHandler(self.bot)
            await error_handler.post_error(e)

    @random_encounter_task.after_loop
    async def on_task_cancel(self):
        if self.random_encounter_task.is_being_cancelled():
            self.logger.error(
                "sys",
                f"Encounter Loop forcefully stopped. next iteration: {self.random_encounter_task.next_iteration}",
                cog=self.__cog_name__,
            )

    @random_low_lvl_encounter_task.after_loop
    async def on_low_lvl_task_cancel(self):
        if self.random_low_lvl_encounter_task.is_being_cancelled():
            self.logger.error(
                "sys",
                f"Low lvl encounter Loop forcefully stopped. next iteration: {self.random_low_lvl_encounter_task.next_iteration}",
                cog=self.__cog_name__,
            )

    @random_low_lvl_encounter_task.before_loop
    async def random_low_lvl_encounter_task_before(self):
        self.logger.log(
            "sys",
            "Random low lvl Encounter before loop started.",
            cog=self.__cog_name__,
        )
        try:
            for guild in self.bot.guilds:
                if not await self.settings_manager.get_combat_enabled(guild.id):
                    continue

                if len(await self.settings_manager.get_combat_channels(guild.id)) <= 0:
                    continue

                max_encounter_level = await self.database.get_guild_level(guild.id) - 1
                max_encounter_level = max(1, max_encounter_level)

                if max_encounter_level <= 0:
                    continue

                encounter_event = await self.database.get_last_encounter_spawn_event(
                    guild.id, max_lvl=max_encounter_level
                )
                last_spawn = datetime.datetime.now()

                if encounter_event is None:
                    self.logger.log(
                        guild.id,
                        "No previous low lvl spawns, next spawn imminent.",
                        cog=self.__cog_name__,
                    )
                    self.enemy_timers_low_lvl[guild.id] = last_spawn
                    continue

                if encounter_event is not None:
                    last_spawn = encounter_event.datetime

                diff = datetime.datetime.now() - last_spawn
                diff_minutes = int(diff.total_seconds() / 60)
                self.logger.log(
                    guild.id,
                    f"Last lwo lvl spawn was {diff_minutes} minutes ago.",
                    cog=self.__cog_name__,
                )

                min_wait = self.LOW_LVL_ENCOUNTER_MIN_WAIT
                if diff_minutes < self.LOW_LVL_ENCOUNTER_MAX_WAIT:
                    min_wait = max(self.LOW_LVL_ENCOUNTER_MIN_WAIT, diff_minutes)

                next_drop_delay = random.randint(
                    min_wait, self.LOW_LVL_ENCOUNTER_MAX_WAIT
                )
                self.logger.log(
                    guild.id,
                    f"Random low lvl spawn delay: {next_drop_delay} minutes.",
                    cog=self.__cog_name__,
                )
                next_spawn = last_spawn + datetime.timedelta(minutes=next_drop_delay)
                diff = next_spawn - datetime.datetime.now()
                self.logger.log(
                    guild.id,
                    f"Next low lvl spawn in {int(diff.total_seconds()/60)} minutes.",
                    cog=self.__cog_name__,
                )

                self.enemy_timers_low_lvl[guild.id] = next_spawn
        except Exception as e:
            print(traceback.format_exc())
            error_handler = ErrorHandler(self.bot)
            await error_handler.post_error(e)

    async def enemy_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        enemies = [await self.factory.get_enemy(enum) for enum in EnemyType]

        choices = [
            app_commands.Choice(
                name=enemy.name,
                value=enemy.type,
            )
            for enemy in enemies
            if current.lower() in enemy.name.lower()
        ][:25]
        return choices

    async def base_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        gear_base_types = [base_type for base_type in GearBaseType]
        skill_base_types = [base_type for base_type in SkillType]
        enchantment_base_types = [base_type for base_type in EnchantmentType]
        base_types = gear_base_types + skill_base_types + enchantment_base_types
        bases = [await self.factory.get_base(enum) for enum in base_types]

        bases = [base for base in bases if base.droppable and base.name != ""]

        choices = [
            app_commands.Choice(
                name=base.name,
                value=base.type,
            )
            for base in bases
            if current.lower() in base.name.lower()
        ][:25]
        return choices

    @app_commands.command(
        name="spawn_encounter",
        description="Manually spawn a random minor encounter in a beans channel. (Admin only)",
    )
    @app_commands.check(__has_permission)
    @app_commands.autocomplete(enemy_type=enemy_autocomplete)
    @app_commands.guild_only()
    async def spawn_encounter(
        self,
        interaction: discord.Interaction,
        enemy_type: str | None,
        level: int | None,
    ):
        await interaction.response.defer(ephemeral=True)

        if not await self.__check_enabled(interaction):
            return

        guild_id = interaction.guild_id

        if level is not None:
            guild_level = await self.database.get_guild_level(guild_id)
            level = max(1, min(guild_level, level))

        if enemy_type is not None:  # noqa: SIM102
            try:
                enemy_type = EnemyType(enemy_type)
            except Exception:
                await self.bot.command_response(
                    self.__cog_name__,
                    interaction,
                    "Enemy not found.",
                    args=[enemy_type],
                )
                return

            enemy = await self.factory.get_enemy(enemy_type)

            if level is not None:
                level = max(enemy.min_level, level)
                level = min(enemy.max_level, level)

        combat_channels = await self.settings_manager.get_combat_channels(
            interaction.guild_id
        )
        if len(combat_channels) == 0:
            await self.bot.command_response(
                self.__cog_name__, interaction, "Error: No combat channel set."
            )

        await self.encounter_manager.spawn_encounter(
            interaction.guild, enemy_type, level
        )
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            "Encounter successfully spawned.",
            ephemeral=True,
        )

        await self.__reevaluate_next_enemy(interaction.guild.id)
        await self.__reevaluate_next_low_lvl_enemy(interaction.guild.id)

    @app_commands.command(
        name="equipment",
        description="Manage your combat equipment and skills.",
    )
    @app_commands.guild_only()
    async def equipment(
        self, interaction: discord.Interaction, user: discord.User | None
    ):
        if not await self.__check_enabled(interaction):
            return
        if not await self.__beans_role_check(interaction):
            return

        guild_id = interaction.guild_id

        log_message = (
            f"{interaction.user.name} used command `{interaction.command.name}`."
        )
        self.logger.log(interaction.guild_id, log_message, cog=self.__cog_name__)
        await interaction.response.defer(ephemeral=True)

        scrap_balance = 0

        if user is None:
            user = interaction.user
            user_items = await self.database.get_item_counts_by_user(
                guild_id, user.id, item_types=[ItemType.SCRAP]
            )
            if ItemType.SCRAP in user_items:
                scrap_balance = user_items[ItemType.SCRAP]

        character = await self.actor_manager.get_character(user)

        view = GearMenuView(
            self.controller,
            interaction,
            character,
            scrap_balance,
            limited=(user.id != interaction.user.id),
        )

        embeds = []
        embeds.append(
            EquipmentHeadEmbed(user, is_owner=(user.id == interaction.user.id))
        )

        loading_embed = discord.Embed(
            title="Loading Gear", color=discord.Colour.light_grey()
        )
        self.embed_manager.add_text_bar(loading_embed, "", "Please Wait...")
        loading_embed.set_thumbnail(url=self.bot.user.display_avatar)
        embeds.append(loading_embed)

        message = await interaction.followup.send("", embeds=embeds, view=view)
        view.set_message(message)
        await view.refresh_ui()

    group = app_commands.Group(
        name="combat", description="Subcommands for the combat module."
    )

    @group.command(
        name="auto_scrap",
        description="Automatically scrap all loot up to and including this level.",
    )
    @app_commands.guild_only()
    async def auto_scrap(
        self,
        interaction: discord.Interaction,
        level: app_commands.Range[int, 0],
    ):
        if not await self.__check_enabled(interaction, all_channels=True):
            return
        await interaction.response.defer(ephemeral=True)

        member_id = interaction.user.id
        guild_id = interaction.guild_id

        await self.user_settings_manager.set(
            member_id, guild_id, UserSettingType.AUTO_SCRAP, level
        )

        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"Auto scrapping enabled for loot of level {level} and below.",
            ephemeral=True,
            args=[level],
        )

    @group.command(
        name="give_loot",
        description="Give specific loot.",
    )
    @app_commands.autocomplete(base=base_autocomplete)
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def give_loot(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        base: str,
        rarity: Rarity | None,
        level: app_commands.Range[int, 1] | None,
        amount: app_commands.Range[int, 1, 9] | None,
    ):
        if not await self.__check_enabled(interaction, all_channels=True):
            return
        await interaction.response.defer()

        member_id = user.id
        guild_id = interaction.guild_id

        if amount is None:
            amount = 1

        if level is None:
            level = await self.database.get_guild_level(guild_id)

        if rarity is None:
            rarity = Rarity.LEGENDARY

        embeds = []

        for _ in range(amount):
            droppable_base = await self.factory.get_base(base)

            gear = await self.gear_manager.generate_specific_drop(
                member_id=member_id,
                guild_id=guild_id,
                item_level=level,
                base=droppable_base,
                rarity=rarity,
            )

            embed = gear.get_embed()
            embeds.append(embed)

        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"Loot was given out to {user.display_name}",
            embeds=embeds,
        )

    @group.command(
        name="reload_overview",
        description="Reloads combat overview.",
    )
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def reload_overview(self, interaction: discord.Interaction):
        if not await self.__check_enabled(interaction, all_channels=True):
            return

        await interaction.response.defer()
        await self.discord.refresh_combat_messages(interaction.guild_id, purge=True)

        await self.bot.command_response(
            self.__cog_name__, interaction, "Successfully reloaded combats."
        )

    @group.command(
        name="debug",
        description="Used for development and testing",
    )
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def debug(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        output = ""

        guild_id = interaction.guild_id
        if guild_id in self.enemy_timers:
            output += (
                f"Enemy Timer: <t:{int(self.enemy_timers[guild_id].timestamp())}:R>"
            )
        if guild_id in self.enemy_timers_low_lvl:
            output += f"Enemy Timer low lvl: <t:{int(self.enemy_timers_low_lvl[guild_id].timestamp())}:R>"

        await self.bot.command_response(self.__cog_name__, interaction, output)

        output = "\n\nEnemy_potencies:"
        for enemy_type in EnemyType:
            enemy = await self.factory.get_enemy(enemy_type)
            skills = []
            for skill_type in enemy.skill_types:
                skill = await self.factory.get_enemy_skill(skill_type)
                skills.append(skill)

            output += f"\n\n{enemy.name}"

            avg_potency = self.get_potency_per_turn(enemy, skills, 1)
            output += f"\ncurrent: {avg_potency}"

            avg_potency = self.get_potency_per_turn(enemy, skills, 2)
            output += f"\nbase health: {avg_potency}"

            avg_potency = self.get_potency_per_turn(enemy, skills, 3)
            output += f"\nhealth+1: {avg_potency}"

            avg_potency = self.get_potency_per_turn(enemy, skills, 4)
            output += f"\ndmg: {avg_potency}"

            avg_potency = self.get_potency_per_turn(enemy, skills, 5)
            output += f"\ndmg*2: {avg_potency}"

        self.logger.log(guild_id, output)

    def get_potency_per_turn(self, enemy: Enemy, skills: list[Skill], mode: int):
        sorted_skills = sorted(
            skills,
            key=lambda x: (
                x.base_skill.base_value
                if x.base_skill.skill_effect != SkillEffect.HEALING
                else 100
            ),
            reverse=True,
        )
        match mode:
            case 1:
                max_depth = enemy.health * 2
            case 2:
                max_depth = enemy.health
            case 3:
                max_depth = enemy.health + 1
            case 4:
                max_depth = enemy.damage_scaling
            case 5:
                max_depth = enemy.damage_scaling * 2

        cooldowns: dict[SkillType, int] = {}
        initial_state: dict[SkillType, int] = {}

        for skill in sorted_skills:
            cooldowns[skill.base_skill.type] = skill.base_skill.cooldown
            initial_state[skill.base_skill.type] = 0
            if skill.base_skill.initial_cooldown is not None:
                initial_state[skill.base_skill.type] = skill.base_skill.initial_cooldown

        state_list: list[dict[SkillType, int]] = []
        skill_count = Counter()

        def get_rotation(
            state_list: list[dict[SkillType, int]],
            skill_count: Counter,
            state: dict[SkillType, int],
            depth_check: int,
        ) -> list[dict[SkillType, int]]:
            if depth_check <= 0:
                return

            state_list.append(state)

            next_state: dict[SkillType, int] = {}

            skills_chosen = 0

            for skill_type, cooldown in state.items():
                if cooldown <= 0 and skills_chosen < enemy.actions_per_turn:
                    next_state[skill_type] = cooldowns[skill_type]
                    skill_count[skill_type] += 1
                    skills_chosen += 1
                    continue

                next_state[skill_type] = max(0, cooldown - 1)

            if skills_chosen == 0:
                raise StopIteration("No available skill found.")

            get_rotation(state_list, skill_count, next_state, (depth_check - 1))

        get_rotation(state_list, skill_count, initial_state, max_depth)

        rotation_length = len(state_list)
        potency = 0

        for skill in sorted_skills:
            base_potency = 0
            if skill.base_skill.skill_effect not in [
                SkillEffect.BUFF,
                SkillEffect.HEALING,
            ]:
                base_potency = skill.base_skill.base_value * skill.base_skill.hits
            potency_per_turn = (
                base_potency
                * skill_count[skill.base_skill.skill_type]
                / rotation_length
            )
            potency += potency_per_turn

        return potency

    @group.command(
        name="settings",
        description="Overview of all combat related settings and their current value.",
    )
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def get_settings(self, interaction: discord.Interaction):

        output = await self.settings_manager.get_settings_string(
            interaction.guild_id, SettingsManager.COMBAT_SUBSETTINGS_KEY
        )
        await self.bot.command_response(self.__cog_name__, interaction, output)

    @group.command(
        name="toggle",
        description="Enable or disable the entire combat module.",
    )
    @app_commands.describe(enabled="Turns the combat module on or off.")
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def set_toggle(
        self, interaction: discord.Interaction, enabled: Literal["on", "off"]
    ):
        await self.settings_manager.set_combat_enabled(
            interaction.guild_id, enabled == "on"
        )
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"Combat module was turned {enabled}.",
            args=[enabled],
        )

    @group.command(
        name="add_combat_channel",
        description="Add a channel to spawn encounters in.",
    )
    @app_commands.describe(channel="This channel will be added to the combat channels.")
    @app_commands.check(__has_permission)
    async def add_combat_channel(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ):
        await self.settings_manager.add_combat_channel(interaction.guild_id, channel.id)
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"Added {channel.name} to combat channels.",
            args=[channel.name],
        )
        await self.discord.refresh_combat_messages(interaction.guild_id, purge=True)

    @group.command(
        name="remove_combat_channel",
        description="Remove a channel to from the combat channels.",
    )
    @app_commands.describe(
        channel="This channel will be removed from the combat channels."
    )
    @app_commands.check(__has_permission)
    async def remove_combat_channel(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ):
        await self.settings_manager.remove_combat_channel(
            interaction.guild_id, channel.id
        )
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"Removed {channel.name} from combat channels.",
            args=[channel.name],
        )

    @group.command(
        name="setup",
        description="Opens a dialog to edit various combat settings.",
    )
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def gamba_setup(self, interaction: discord.Interaction) -> None:
        guild_id = interaction.guild_id
        modal = SettingsModal(
            self.bot,
            self.settings_manager,
            self.__cog_name__,
            interaction.command.name,
            "Settings for Combat related Features",
            callback=self.discord.refresh_combat_messages,
            callback_arguments=[guild_id],
        )

        await modal.add_field(
            guild_id,
            SettingsManager.COMBAT_SUBSETTINGS_KEY,
            SettingsManager.COMBAT_MAX_LVL_SPAWN_START_TIME_KEY,
            int,
        )
        await modal.add_field(
            guild_id,
            SettingsManager.COMBAT_SUBSETTINGS_KEY,
            SettingsManager.COMBAT_MAX_LVL_SPAWN_END_TIME_KEY,
            int,
        )

        modal.add_constraint(
            [SettingsManager.COMBAT_MAX_LVL_SPAWN_START_TIME_KEY],
            lambda a: a <= 23 and a >= 0,
            "Start hour must be between 0 and 23",
        )

        modal.add_constraint(
            [SettingsManager.COMBAT_MAX_LVL_SPAWN_END_TIME_KEY],
            lambda a: a <= 23 and a >= 0,
            "End hour must be between 0 and 23",
        )

        await interaction.response.send_modal(modal)

    @group.command(
        name="set_ping_role",
        description="This role will be pinged with each encounter spawn.",
    )
    @app_commands.describe(role="The role to be pinged.")
    @app_commands.check(__has_permission)
    async def set_ping_role(self, interaction: discord.Interaction, role: discord.Role):
        await self.settings_manager.set_spawn_ping_role(interaction.guild_id, role.id)
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"Encounter ping role was set to `{role.name}` .",
            args=[role.name],
        )

    @group.command(
        name="set_max_lvl_ping_role",
        description="This role will be pinged when a max lvl encounter spawns.",
    )
    @app_commands.describe(role="The role to be pinged.")
    @app_commands.check(__has_permission)
    async def set_max_lvl_ping_role(
        self, interaction: discord.Interaction, role: discord.Role
    ):
        await self.settings_manager.set_max_lvl_spawn_ping_role(
            interaction.guild_id, role.id
        )
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"Max lvl encounter ping role was set to `{role.name}` .",
            args=[role.name],
        )

    @group.command(
        name="force_reload",
        description="foces a encounter reload.",
    )
    @app_commands.check(__has_permission)
    async def force_reload(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        channel_id = interaction.channel_id
        guild_id = interaction.guild_id

        if channel_id is None:
            await self.bot.command_response(
                self.__cog_name__,
                interaction,
                "Please use this command inside an encounter thread.",
                ephemeral=True,
            )
            return

        encounter = await self.database.get_encounter_by_thread_id(guild_id, channel_id)

        if encounter is None:
            await self.bot.command_response(
                self.__cog_name__,
                interaction,
                "No encounter found for this thread.",
                ephemeral=True,
            )
            return

        await self.encounter_manager.reload_encounter(encounter.id)

        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            "Forced Encounter Reload.",
            ephemeral=True,
        )

    @group.command(
        name="force_end",
        description="Foces a encounter to end.",
    )
    @app_commands.check(__has_permission)
    async def force_end(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        channel_id = interaction.channel_id
        guild_id = interaction.guild_id

        if channel_id is None:
            await self.bot.command_response(
                self.__cog_name__,
                interaction,
                "Please use this command inside an encounter thread.",
                ephemeral=True,
            )
            return

        encounter = await self.database.get_encounter_by_thread_id(guild_id, channel_id)

        if encounter is None:
            await self.bot.command_response(
                self.__cog_name__,
                interaction,
                "No encounter found for this thread.",
                ephemeral=True,
            )
            return

        event = EncounterEvent(
            datetime.datetime.now(),
            guild_id,
            encounter.id,
            interaction.user.id,
            EncounterEventType.END,
        )
        await self.controller.dispatch_event(event)

        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            "Forced Encounter End.",
            ephemeral=True,
        )

    @group.command(
        name="force_start",
        description="Foces a encounter to start even when the participant requirements are not met.",
    )
    @app_commands.check(__has_permission)
    async def force_start(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        channel_id = interaction.channel_id
        guild_id = interaction.guild_id

        if channel_id is None:
            await self.bot.command_response(
                self.__cog_name__,
                interaction,
                "Please use this command inside an encounter thread.",
                ephemeral=True,
            )
            return

        encounter = await self.database.get_encounter_by_thread_id(guild_id, channel_id)

        if encounter is None:
            await self.bot.command_response(
                self.__cog_name__,
                interaction,
                "No encounter found for this thread.",
                ephemeral=True,
            )
            return

        event = UIEvent(
            UIEventType.COMBAT_INITIATE,
            encounter,
        )
        await self.controller.dispatch_ui_event(event)

        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            "Forced Encounter Start.",
            ephemeral=True,
        )

    @group.command(
        name="force_skip",
        description="Foces a encounter to start even when the participant requirements are not met.",
    )
    @app_commands.check(__has_permission)
    async def force_action(self, interaction: discord.Interaction, action: int):
        channel_id = interaction.channel_id
        guild_id = interaction.guild_id

        if channel_id is None:
            await self.bot.command_response(
                self.__cog_name__,
                interaction,
                "Please use this command inside an encounter thread.",
                ephemeral=True,
            )
            return

        encounter = await self.database.get_encounter_by_thread_id(guild_id, channel_id)

        if encounter is None:
            await self.bot.command_response(
                self.__cog_name__,
                interaction,
                "No encounter found for this thread.",
                ephemeral=True,
            )
            return

        event = UIEvent(
            UIEventType.COMBAT_FORCE_USE,
            (interaction, action),
        )
        await self.controller.dispatch_ui_event(event)


async def setup(bot):
    await bot.add_cog(Combat(bot))
