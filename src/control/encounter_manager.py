import datetime
import random

import discord
from bot_util import BotUtil
from combat.encounter import Encounter
from combat.enemies import *  # noqa: F403
from combat.enemies.enemy import Enemy
from combat.enemies.types import EnemyType
from datalayer.database import Database
from discord.ext import commands
from events.bot_event import BotEvent
from items import ChestBeansReward
from items.item import Item

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
        pass

    def get_enemy(self, enemy_type: EnemyType) -> Enemy:
        enemy = globals()[enemy_type]
        instance = enemy()
        return instance

    async def create_encounter(self, guild_id: int):
        encounter_level = 5  # TODO: get guild encounter level
        enemies = [self.get_enemy(enemy_type) for enemy_type in EnemyType]
        possible_enemies = [
            enemy for enemy in enemies if enemy.level <= encounter_level
        ]

        spawn_weights = [enemy.weight for enemy in possible_enemies]
        spawn_weights = [1.0 / w for w in spawn_weights]
        sum_weights = sum(spawn_weights)
        spawn_weights = [w / sum_weights for w in spawn_weights]

        enemy = random.choices(possible_enemies, weights=spawn_weights)[0]
        enemy_health = random.randint(enemy.min_hp, enemy.max_hp)

        return Encounter(enemy, enemy_health)

    async def spawn_encounter(self, guild: discord.Guild, channel_id: int):
        log_message = f"Encounter was spawned in {guild.name}."
        self.logger.log(guild.id, log_message, cog=self.log_name)

        encounter = await self.create_encounter(guild.id)
        embed = encounter.get_embed()

        view = LootBoxView(self.controller)
        image = discord.File(
            f"./img/enemies/{encounter.enemy.image}", encounter.enemy.image
        )
        channel = guild.get_channel(channel_id)

        message = await channel.send("", embed=embed, view=view, files=[image])

        encounter_id = await self.database.log_encounter(encounter)

        event = LootBoxEvent(
            datetime.datetime.now(),
            guild.id,
            encounter_id,
            self.bot.user.id,
            LootBoxEventType.DROP,
        )
        await self.controller.dispatch_event(event)
