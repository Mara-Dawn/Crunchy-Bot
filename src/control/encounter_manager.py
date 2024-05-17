import datetime
import random

import discord
from combat.encounter import Encounter
from combat.enemies import *  # noqa: F403
from combat.enemies.enemy import Enemy
from combat.enemies.types import EnemyType
from datalayer.database import Database
from discord.ext import commands
from events.bot_event import BotEvent
from events.encounter_event import EncounterEvent
from events.types import EncounterEventType, EventType
from view.combat.engage_view import EnemyEngageView

from control.controller import Controller
from control.item_manager import ItemManager
from control.logger import BotLogger
from control.service import Service
from control.settings_manager import SettingsManager


class EncounterManager(Service):

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
        self.item_manager: ItemManager = self.controller.get_service(ItemManager)
        self.log_name = "Encounter"

    async def listen_for_event(self, event: BotEvent):
        match event.type:
            case EventType.ENCOUNTER:
                encounter_event: EncounterEvent = event
                match encounter_event.encounter_event_type:
                    case EncounterEventType.MEMBER_ENGAGE:
                        await self.add_member_to_encounter(
                            encounter_event.encounter_id, encounter_event.member_id
                        )

    def get_enemy(self, enemy_type: EnemyType) -> Enemy:
        enemy = globals()[enemy_type]
        instance = enemy()
        return instance

    async def create_encounter(self, guild_id: int):
        encounter_level = await self.database.get_guild_level(guild_id)

        enemies = [self.get_enemy(enemy_type) for enemy_type in EnemyType]
        possible_enemies = [
            enemy for enemy in enemies if enemy.level <= encounter_level
        ]

        spawn_weights = [enemy.weighting for enemy in possible_enemies]
        spawn_weights = [1.0 / w for w in spawn_weights]
        sum_weights = sum(spawn_weights)
        spawn_weights = [w / sum_weights for w in spawn_weights]

        enemy = random.choices(possible_enemies, weights=spawn_weights)[0]
        enemy_health = random.randint(enemy.min_hp, enemy.max_hp)

        return Encounter(guild_id, enemy.type, enemy_health)

    async def get_embed(
        self, encounter: Encounter, show_info: bool = False
    ) -> discord.Embed:
        enemy = self.get_enemy(encounter.enemy_type)
        title = "A random Enemy appeared!"

        embed = discord.Embed(title=title, color=discord.Colour.blurple())

        enemy_name = f"> ~* {enemy.name} *~"
        content = f'```python\n"{enemy.description}"```'
        embed.add_field(name=enemy_name, value=content, inline=False)

        if show_info:
            enemy_info = f"```ansi\n[37m{enemy.information}```"
            embed.add_field(name="", value=enemy_info, inline=False)
            return embed

        health = f"**health:** {encounter.current_health}/{encounter.max_health}\n"
        embed.add_field(name="", value=health, inline=False)

        embed.set_image(url=f"attachment://{enemy.image}")

        return embed

    async def spawn_encounter(self, guild: discord.Guild, channel_id: int):
        log_message = f"Encounter was spawned in {guild.name}."
        self.logger.log(guild.id, log_message, cog=self.log_name)

        encounter = await self.create_encounter(guild.id)
        embed = await self.get_embed(encounter)

        enemy = self.get_enemy(encounter.enemy_type)

        view = EnemyEngageView(self.controller)
        image = discord.File(f"./img/enemies/{enemy.image}", enemy.image)
        channel = guild.get_channel(channel_id)

        message = await channel.send("", embed=embed, view=view, files=[image])
        encounter.message_id = message.id

        encounter_id = await self.database.log_encounter(encounter)

        event = EncounterEvent(
            datetime.datetime.now(),
            guild.id,
            encounter_id,
            self.bot.user.id,
            EncounterEventType.SPAWN,
        )
        await self.controller.dispatch_event(event)

    async def add_member_to_encounter(self, encounter_id: int, member_id: int):
        pass
