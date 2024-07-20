import datetime
import random
import secrets
from typing import Literal

import discord
from bot import CrunchyBot
from combat.enemies.types import EnemyType
from combat.gear.types import GearBaseType, Rarity
from combat.skills.types import SkillType
from control.combat.combat_actor_manager import CombatActorManager
from control.combat.combat_embed_manager import CombatEmbedManager
from control.combat.combat_gear_manager import CombatGearManager
from control.combat.encounter_manager import EncounterManager
from control.combat.object_factory import ObjectFactory
from control.controller import Controller
from control.logger import BotLogger
from control.settings_manager import SettingsManager
from datalayer.database import Database
from discord import app_commands
from discord.ext import commands, tasks
from items.types import ItemType
from view.combat.embed import EquipmentHeadEmbed
from view.combat.equipment_view import EquipmentView


class Combat(commands.Cog):

    ENCOUNTER_MIN_WAIT = 45
    ENCOUNTER_MAX_WAIT = 75

    LOW_LVL_ENCOUNTER_MIN_WAIT = 20
    LOW_LVL_ENCOUNTER_MAX_WAIT = 40

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
        self.gear_manager: CombatGearManager = self.controller.get_service(
            CombatGearManager
        )
        self.embed_manager: CombatEmbedManager = self.controller.get_service(
            CombatEmbedManager
        )
        self.actor_manager: CombatActorManager = self.controller.get_service(
            CombatActorManager
        )
        self.factory: ObjectFactory = self.controller.get_service(ObjectFactory)
        self.enemy_timers = {}
        self.enemy_timers_low_lvl = {}

    @staticmethod
    async def __has_permission(interaction: discord.Interaction) -> bool:
        author_id = 90043934247501824
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
            await self.encounter_manager.refresh_combat_messages(guild.id)
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

        for guild in self.bot.guilds:
            if guild.id not in self.enemy_timers:
                continue

            if datetime.datetime.now() < self.enemy_timers[guild.id]:
                continue

            if not await self.settings_manager.get_combat_enabled(guild.id):
                continue

            self.logger.log("sys", "Enemy timeout reached.", cog=self.__cog_name__)
            await self.__reevaluate_next_enemy(guild.id)

            combat_channels = await self.settings_manager.get_combat_channels(guild.id)
            if len(combat_channels) == 0:
                continue

            encounter_level = await self.database.get_guild_level(guild.id)

            await self.encounter_manager.spawn_encounter(
                guild, secrets.choice(combat_channels), level=encounter_level
            )

    @tasks.loop(minutes=1)
    async def random_low_lvl_encounter_task(self):
        self.logger.debug(
            "sys", "Random low lvl Encounter task started.", cog=self.__cog_name__
        )

        for guild in self.bot.guilds:
            if guild.id not in self.enemy_timers_low_lvl:
                continue

            max_encounter_level = await self.database.get_guild_level(guild.id) - 1
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

            combat_channels = await self.settings_manager.get_combat_channels(guild.id)
            if len(combat_channels) == 0:
                continue

            encounter_level = random.randint(1, max_encounter_level)

            await self.encounter_manager.spawn_encounter(
                guild, secrets.choice(combat_channels), level=encounter_level
            )

    @random_encounter_task.before_loop
    async def random_encounter_task_before(self):
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

    @random_low_lvl_encounter_task.before_loop
    async def random_low_lvl_encounter_task_before(self):
        self.logger.log(
            "sys",
            "Random low lvl Encounter before loop started.",
            cog=self.__cog_name__,
        )

        for guild in self.bot.guilds:
            if not await self.settings_manager.get_combat_enabled(guild.id):
                continue

            if len(await self.settings_manager.get_combat_channels(guild.id)) <= 0:
                continue

            max_encounter_level = await self.database.get_guild_level(guild.id) - 1

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

            next_drop_delay = random.randint(min_wait, self.LOW_LVL_ENCOUNTER_MAX_WAIT)
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
        base_types = gear_base_types + skill_base_types
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

        if enemy_type is not None:
            if enemy_type not in EnemyType._value2member_map_:
                await self.bot.command_response(
                    self.__cog_name__,
                    interaction,
                    "Enemy not found.",
                    args=[enemy_type],
                )
                return

            if level is not None:
                enemy = await self.factory.get_enemy(enemy_type)

                if enemy.min_level > level or enemy.max_level < level:
                    await self.bot.command_response(
                        self.__cog_name__,
                        interaction,
                        "Enemy cannot have that level.",
                        args=[enemy_type],
                    )
                    return

        combat_channels = await self.settings_manager.get_combat_channels(
            interaction.guild_id
        )
        if len(combat_channels) == 0:
            await self.bot.command_response(
                self.__cog_name__, interaction, "Error: No combat channel set."
            )

        await self.encounter_manager.spawn_encounter(
            interaction.guild, secrets.choice(combat_channels), enemy_type, level
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
    async def equipment(self, interaction: discord.Interaction):
        if not await self.__check_enabled(interaction):
            return

        guild_id = interaction.guild_id
        member_id = interaction.user.id

        log_message = (
            f"{interaction.user.name} used command `{interaction.command.name}`."
        )
        self.logger.log(interaction.guild_id, log_message, cog=self.__cog_name__)
        await interaction.response.defer(ephemeral=True)

        character = await self.actor_manager.get_character(interaction.user)

        user_items = await self.database.get_item_counts_by_user(
            guild_id, member_id, item_types=[ItemType.SCRAP]
        )
        scrap_balance = 0
        if ItemType.SCRAP in user_items:
            scrap_balance = user_items[ItemType.SCRAP]

        guild_level = await self.controller.database.get_guild_level(guild_id)

        view = EquipmentView(
            self.controller, interaction, character, scrap_balance, guild_level
        )

        embeds = []
        embeds.append(EquipmentHeadEmbed(interaction.user))

        loading_embed = discord.Embed(
            title="Loadin Gear", color=discord.Colour.light_grey()
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
        level: app_commands.Range[int, 1],
        base: str,
        rarity: Rarity,
    ):
        if not await self.__check_enabled(interaction, all_channels=True):
            return
        await interaction.response.defer()

        member_id = user.id
        guild_id = interaction.guild_id

        droppable_base = await self.factory.get_base(base)

        gear = await self.gear_manager.generate_specific_drop(
            member_id=member_id,
            guild_id=guild_id,
            item_level=level,
            base=droppable_base,
            rarity=rarity,
        )

        embed = gear.get_embed()

        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"Loot was given out to {user.display_name}",
            embeds=[embed],
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
        await self.encounter_manager.refresh_combat_messages(interaction.guild_id)

        await self.bot.command_response(
            self.__cog_name__, interaction, "Successfully reloaded combats."
        )

    @group.command(
        name="settings",
        description="Overview of all combat related settings and their current value.",
    )
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def get_settings(self, interaction: discord.Interaction):

        # for enemy_type in EnemyType:
        #     enemy = await self.factory.get_enemy(enemy_type)
        #     opponent = await self.actor_manager.get_opponent(
        #         enemy,
        #         3,
        #         100,
        #         [],
        #         [],
        #         {},
        #     )
        #     test_a = opponent.get_potency_per_turn()
        #
        #     log_message = f"\n {enemy.name}:\n"
        #     log_message += f"  old: {test_a}\n"
        #     self.logger.log(interaction.guild_id, log_message, cog=self.__cog_name__)

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
        await self.encounter_manager.refresh_combat_messages(interaction.guild_id)

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


async def setup(bot):
    await bot.add_cog(Combat(bot))
