import datetime
import random
import secrets

import discord
from bot import CrunchyBot
from control.encounter_manager import EncounterManager
from discord import app_commands
from discord.ext import commands, tasks


class Combat(commands.Cog):

    ENCOUNTER_MIN_WAIT = 60
    ENCOUNTER_MAX_WAIT = 90

    def __init__(self, bot: CrunchyBot) -> None:
        super().__init__(bot)
        self.encounter_manager: EncounterManager = self.controller.get_service(
            EncounterManager
        )
        self.enemy_timers = {}

    @staticmethod
    async def __has_permission(interaction: discord.Interaction) -> bool:
        author_id = 90043934247501824
        return (
            interaction.user.id == author_id
            or interaction.user.guild_permissions.administrator
        )

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

    @commands.Cog.listener("on_ready")
    async def on_ready_combat(self):
        self.random_encounter_task.start()
        self.logger.log("init", "Combat loaded.", cog=self.__cog_name__)

    @commands.Cog.listener("on_guild_join")
    async def on_guild_join_combat(self, guild):
        self.logger.log(
            guild.id, "Adding enemy timer for new guild.", cog=self.__cog_name__
        )
        await self.__reevaluate_next_enemy(guild.id)

    @commands.Cog.listener("on_guild_remove")
    async def on_guild_remove_combat(self, guild):
        del self.enemy_timers[guild.id]

    @tasks.loop(minutes=1)
    async def random_encounter_task(self):
        self.logger.log("sys", "Random Encounter task started.", cog=self.__cog_name__)

        for guild in self.bot.guilds:
            if datetime.datetime.now() < self.enemy_timers[guild.id]:
                continue

            self.logger.log("sys", "Enemy timeout reached.", cog=self.__cog_name__)
            await self.__reevaluate_next_enemy(guild.id)

            bean_channels = await self.settings_manager.get_beans_channels(guild.id)
            if len(bean_channels) == 0:
                continue
            await self.encounter_manager.spawn_encounter(
                guild, secrets.choice(bean_channels)
            )

    @random_encounter_task.before_loop
    async def random_encounter_task_before(self):
        self.logger.log(
            "sys", "Random Encounter before loop started.", cog=self.__cog_name__
        )

        for guild in self.bot.guilds:
            # loot_box_event = await self.database.get_last_loot_box_event(guild.id)
            last_spawn = datetime.datetime.now()

            if loot_box_event is not None:
                last_spawn = loot_box_event.datetime

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

    @app_commands.command(
        name="spawn_encounter",
        description="Manually spawn a random minor encounter in a beans channel. (Admin only)",
    )
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def spawn_encounter(self, interaction: discord.Interaction):
        bean_channels = await self.settings_manager.get_beans_channels(
            interaction.guild_id
        )
        if len(bean_channels) == 0:
            await self.bot.command_response(
                self.__cog_name__, interaction, "Error: No beans channel set."
            )

        await self.encounter_manager.spawn_encounter(
            interaction.guild, secrets.choice(bean_channels)
        )
        await self.bot.command_response(
            self.__cog_name__, interaction, "Encounter successfully spawned."
        )
        await self.__reevaluate_next_enemy(interaction.guild.id)


async def setup(bot):
    await bot.add_cog(Combat(bot))
