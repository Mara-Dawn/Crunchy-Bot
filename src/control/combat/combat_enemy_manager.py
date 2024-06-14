from combat.enemies import *  # noqa: F403
from combat.enemies.enemy import Enemy
from combat.enemies.types import EnemyType
from control.controller import Controller
from control.logger import BotLogger
from control.service import Service
from datalayer.database import Database
from discord.ext import commands
from events.bot_event import BotEvent


class CombatEnemyManager(Service):

    def __init__(
        self,
        bot: commands.Bot,
        logger: BotLogger,
        database: Database,
        controller: Controller,
    ):
        super().__init__(bot, logger, database)
        self.controller = controller
        self.log_name = "Combat Enemies"

    async def listen_for_event(self, event: BotEvent):
        pass

    def get_enemy(self, enemy_type: EnemyType) -> Enemy:
        enemy = globals()[enemy_type]
        instance = enemy()
        return instance
